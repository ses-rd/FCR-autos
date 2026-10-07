# -*- coding: utf-8 -*-

from odoo import fields, models

from .sale_order import MONTHS_ES


class AccountMove(models.Model):
    _inherit = "account.move"

    def _get_sale_receipt_date_text(self):
        self.ensure_one()
        receipt_date = self.invoice_date or fields.Date.context_today(self)
        return f"{receipt_date.day} de {MONTHS_ES[receipt_date.month]} del {receipt_date.year}"

    def _get_sale_receipt_sale_order(self):
        self.ensure_one()
        sale_lines = self.invoice_line_ids.mapped("sale_line_ids")
        return sale_lines.mapped("order_id")[:1]

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

        return {
            "brand": brand.name if brand else "",
            "model": model.name if model else product.display_name if product else "",
            "year": vehicle.model_year if vehicle and "model_year" in vehicle._fields else "",
            "license_plate": vehicle.license_plate if vehicle else "",
            "chassis": vehicle.vin_sn if vehicle and "vin_sn" in vehicle._fields else "",
            "mileage": vehicle.odometer if vehicle and "odometer" in vehicle._fields else "",
            "color": vehicle.color if vehicle and "color" in vehicle._fields else "",
            "type": vehicle.category_id.name if vehicle and "category_id" in vehicle._fields and vehicle.category_id else "",
        }

    def _get_sale_receipt_values(self):
        self.ensure_one()
        partner = self.partner_id
        sale_order = self._get_sale_receipt_sale_order()
        paid_amount = self.amount_total - self.amount_residual
        phone = partner.phone or ""
        if not phone and "mobile" in partner._fields:
            phone = partner.mobile or ""
        exchange_rate = ""
        if sale_order and "manual_currency_exchange_rate" in sale_order._fields and sale_order.manual_currency_exchange_rate:
            exchange_rate = sale_order.manual_currency_exchange_rate
        elif "manual_currency_exchange_rate" in self._fields and self.manual_currency_exchange_rate:
            exchange_rate = self.manual_currency_exchange_rate
        executive = self.invoice_user_id.name if self.invoice_user_id else ""
        if not executive and "user_id" in self._fields and self.user_id:
            executive = self.user_id.name

        return {
            "date_text": self._get_sale_receipt_date_text(),
            "client": partner.name or "",
            "vat": partner.vat or "",
            "phone": phone,
            "email": partner.email or "",
            "vehicle": self._get_sale_receipt_vehicle(),
            "initial_payment": paid_amount,
            "total_cost": self.amount_total,
            "balance": self.amount_residual,
            "currency": self.currency_id,
            "exchange_rate": exchange_rate,
            "executive": executive,
        }
