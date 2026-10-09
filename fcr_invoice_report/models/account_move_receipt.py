# -*- coding: utf-8 -*-

from odoo import fields, models

from .sale_order_receipt import MONTHS_ES


class AccountMove(models.Model):
    _inherit = "account.move"

    def action_print_pdf(self):
        self.ensure_one()
        return self.env.ref("account.account_invoices").report_action(self.id, config=False)

    def action_print_sale_separation_receipt(self):
        self.ensure_one()
        return self.env.ref("fcr_invoice_report.action_report_invoice_separation_receipt").report_action(
            self,
            config=False,
        )

    def _get_sale_receipt_date_text(self):
        self.ensure_one()
        receipt_date = self.invoice_date or fields.Date.context_today(self)
        return f"{receipt_date.day} de {MONTHS_ES[receipt_date.month]} del {receipt_date.year}"

    def _get_sale_receipt_date_text_for(self, receipt_date):
        self.ensure_one()
        receipt_date = fields.Date.to_date(receipt_date)
        return f"{receipt_date.day} de {MONTHS_ES[receipt_date.month]} del {receipt_date.year}"

    def _get_sale_receipt_sale_order(self):
        self.ensure_one()
        sale_lines = self.invoice_line_ids.mapped("sale_line_ids")
        sale_order = sale_lines.mapped("order_id")[:1]
        if sale_order:
            return sale_order

        if self.invoice_origin:
            origins = [
                origin.strip()
                for origin in self.invoice_origin.replace(";", ",").split(",")
                if origin.strip()
            ]
            if origins:
                return self.env["sale.order"].search([("name", "in", origins)], limit=1)
        return self.env["sale.order"]

    def _get_sale_receipt_document_label(self):
        self.ensure_one()
        sale_order = self._get_sale_receipt_sale_order()
        if sale_order and sale_order.state in ("draft", "sent"):
            return sale_order._get_sale_receipt_document_label()
        return "FACTURA"

    def _get_sale_receipt_vehicle(self):
        self.ensure_one()
        sale_order = self._get_sale_receipt_sale_order()
        if sale_order:
            return sale_order._get_sale_receipt_vehicle()

        vehicle = False
        vehicle_line = self.invoice_line_ids.filtered(
            lambda line: line.product_id
            and line.product_id.product_tmpl_id
            and "vehicle_id" in line.product_id.product_tmpl_id._fields
            and line.product_id.product_tmpl_id.vehicle_id
        )[:1]
        if vehicle_line:
            vehicle = vehicle_line.product_id.product_tmpl_id.vehicle_id

        product_line = self.invoice_line_ids.filtered(lambda line: line.product_id)[:1]
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
        sale_order = self._get_sale_receipt_sale_order()
        if sale_order:
            return sale_order._get_sale_receipt_items_text()
        lines = self.invoice_line_ids.filtered(lambda line: not line.display_type)
        return ", ".join(lines.mapped("name"))

    def _get_sale_receipt_exchange_rate(self):
        self.ensure_one()
        sale_order = self._get_sale_receipt_sale_order()
        if sale_order:
            rate = sale_order._get_sale_receipt_exchange_rate()
            if rate:
                return rate
        for field_name in ("manual_currency_exchange_rate", "invoice_currency_rate", "currency_rate", "expected_currency_rate"):
            if field_name in self._fields and self[field_name]:
                return self[field_name]
        return ""

    def _get_sale_receipt_exchange_rate_text(self):
        self.ensure_one()
        dop_payments = self.reconciled_payment_ids.filtered(lambda payment: payment.currency_id.name == "DOP")
        if dop_payments:
            payment = dop_payments.sorted("date", reverse=True)[0]
            paid_document_amount = self.amount_total - self.amount_residual
            if not paid_document_amount:
                paid_document_amount = self.amount_total
            rate = payment.amount / paid_document_amount if paid_document_amount else 0.0
            if rate:
                return f"Tasa del {self._get_sale_receipt_date_text_for(payment.date)}: {rate:.2f}"

        rate = self._get_sale_receipt_exchange_rate()
        if rate and self.currency_id.name == "DOP":
            receipt_date = self.invoice_date or fields.Date.context_today(self)
            return f"Tasa del {self._get_sale_receipt_date_text_for(receipt_date)}: {rate:.2f}"
        return ""

    def _get_sale_receipt_values(self):
        self.ensure_one()
        sale_order = self._get_sale_receipt_sale_order()
        if sale_order and sale_order.state in ("draft", "sent"):
            return sale_order._get_sale_receipt_values()

        partner = self.partner_id
        paid_amount = self.amount_total - self.amount_residual
        phone = partner.phone or ""
        if not phone and "mobile" in partner._fields:
            phone = partner.mobile or ""
        executive = self.invoice_user_id.name if self.invoice_user_id else ""
        if not executive and "user_id" in self._fields and self.user_id:
            executive = self.user_id.name

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
            "balance": self.amount_residual,
            "currency": self.currency_id,
            "exchange_rate": self._get_sale_receipt_exchange_rate(),
            "exchange_rate_text": self._get_sale_receipt_exchange_rate_text(),
            "executive": executive,
        }
