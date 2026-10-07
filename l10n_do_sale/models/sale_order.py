# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.addons.l10n_do_ecf.models.account_move import PAYMENT_METHOD_SELECTION


MONTHS_ES = {
    1: "Enero",
    2: "Febrero",
    3: "Marzo",
    4: "Abril",
    5: "Mayo",
    6: "Junio",
    7: "Julio",
    8: "Agosto",
    9: "Septiembre",
    10: "Octubre",
    11: "Noviembre",
    12: "Diciembre",
}


class SaleOrder(models.Model):
    _inherit = "sale.order"

    l10n_do_ecf_payment_method = fields.Selection(PAYMENT_METHOD_SELECTION, string="e-CF Payment Method",
                                                  compute="_compute_l10n_do_payment_method_id", store=True,
                                                  readonly=False)

    @api.depends("partner_id")
    def _compute_l10n_do_payment_method_id(self):
        default_payment_method_id = "0"
        for order in self:
            if order.country_code == 'DO':
                order.l10n_do_ecf_payment_method = (
                        order.partner_id.l10n_do_ecf_payment_method or
                        order.l10n_do_ecf_payment_method or
                        default_payment_method_id
                )
            else:
                order.l10n_do_ecf_payment_method = False

    def _prepare_invoice(self):
        # EXTENDS 'sale'
        self.ensure_one()
        vals = super()._prepare_invoice()
        if self.country_code != 'DO':
            return vals

        vals['l10n_do_ecf_payment_method'] = self.l10n_do_ecf_payment_method
        return vals

    def _get_sale_receipt_date_text(self):
        self.ensure_one()
        receipt_date = fields.Date.context_today(self)
        if self.date_order:
            receipt_date = fields.Date.to_date(self.date_order)
        return f"{receipt_date.day} de {MONTHS_ES[receipt_date.month]} del {receipt_date.year}"

    def _get_sale_receipt_date_text_for(self, receipt_date):
        self.ensure_one()
        receipt_date = fields.Date.to_date(receipt_date)
        return f"{receipt_date.day} de {MONTHS_ES[receipt_date.month]} del {receipt_date.year}"

    def _get_sale_receipt_vehicle(self):
        self.ensure_one()
        vehicle = False
        vehicle_line = self.order_line.filtered(
            lambda line: line.product_template_id
            and "vehicle_id" in line.product_template_id._fields
            and line.product_template_id.vehicle_id
        )[:1]
        if vehicle_line:
            vehicle = vehicle_line.product_template_id.vehicle_id

        product_line = self.order_line.filtered(lambda line: not line.display_type and line.product_id)[:1]
        product = product_line.product_id if product_line else False
        model = vehicle.model_id if vehicle else False
        brand = model.brand_id if model and "brand_id" in model._fields else False

        vehicle_values = {
            "brand": brand.name if brand else "",
            "model": model.name if model else product.display_name if product else "",
            "year": vehicle.model_year if vehicle and "model_year" in vehicle._fields else "",
            "license_plate": vehicle.license_plate if vehicle else "",
            "chassis": vehicle.vin_sn if vehicle and "vin_sn" in vehicle._fields else "",
            "mileage": vehicle.odometer if vehicle and "odometer" in vehicle._fields else "",
            "color": vehicle.color if vehicle and "color" in vehicle._fields else "",
            "type": vehicle.category_id.name if vehicle and "category_id" in vehicle._fields and vehicle.category_id else "",
        }
        vehicle_values["has_vehicle"] = bool(vehicle) or bool(
            vehicle_values["brand"]
            or vehicle_values["year"]
            or vehicle_values["license_plate"]
            or vehicle_values["chassis"]
            or vehicle_values["mileage"]
            or vehicle_values["color"]
            or vehicle_values["type"]
        )
        return vehicle_values

    def _get_sale_receipt_items_text(self):
        self.ensure_one()
        lines = self.order_line.filtered(lambda line: not line.display_type)
        return ", ".join(lines.mapped("name"))

    def _get_sale_receipt_paid_amount(self):
        self.ensure_one()
        sale_invoices = self.invoice_ids.filtered(
            lambda move: move.state != "cancel" and move.move_type in ("out_invoice", "out_receipt")
        )
        paid_amount = sum(sale_invoices.mapped(lambda move: move.amount_total - move.amount_residual))
        if paid_amount:
            return paid_amount

        downpayment_lines = self.order_line.filtered(
            lambda line: not line.display_type and "is_downpayment" in line._fields and line.is_downpayment
        )
        return sum(downpayment_lines.mapped("price_total"))

    def _get_sale_receipt_exchange_rate(self):
        self.ensure_one()
        if "manual_currency_exchange_rate" in self._fields and self.manual_currency_exchange_rate:
            return self.manual_currency_exchange_rate
        if "currency_rate" in self._fields and self.currency_rate:
            return self.currency_rate
        return ""

    def _get_sale_receipt_exchange_rate_text(self):
        self.ensure_one()
        invoices = self.invoice_ids.filtered(lambda move: move.state != "cancel" and move.move_type in ("out_invoice", "out_receipt"))
        for invoice in invoices:
            rate_text = invoice._get_sale_receipt_exchange_rate_text()
            if rate_text:
                return rate_text
        rate = self._get_sale_receipt_exchange_rate()
        if rate and self.currency_id.name == "DOP":
            receipt_date = self.date_order or fields.Date.context_today(self)
            return f"Tasa del {self._get_sale_receipt_date_text_for(receipt_date)}: {rate:.2f}"
        return ""

    def _get_sale_receipt_document_label(self):
        self.ensure_one()
        if self.state in ("draft", "sent"):
            return "COTIZACIÓN"
        return "RECIBO DE VENTA"

    def _get_sale_receipt_values(self):
        self.ensure_one()
        partner = self.partner_id
        paid_amount = self._get_sale_receipt_paid_amount()
        phone = partner.phone or ""
        if not phone and "mobile" in partner._fields:
            phone = partner.mobile or ""

        return {
            "date_text": self._get_sale_receipt_date_text(),
            "document_label": self._get_sale_receipt_document_label(),
            "company": self.company_id,
            "client": partner.name or "",
            "vat": partner.vat or "",
            "phone": phone,
            "email": partner.email or "",
            "vehicle": self._get_sale_receipt_vehicle(),
            "items_text": self._get_sale_receipt_items_text(),
            "initial_payment": paid_amount,
            "total_cost": self.amount_total,
            "balance": self.amount_total - paid_amount,
            "currency": self.currency_id,
            "exchange_rate": self._get_sale_receipt_exchange_rate(),
            "exchange_rate_text": self._get_sale_receipt_exchange_rate_text(),
            "executive": self.user_id.name or "",
        }
