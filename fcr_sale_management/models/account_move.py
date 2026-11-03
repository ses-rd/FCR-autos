# -*- coding: utf-8 -*-

from odoo import fields, models

from .sale_order import MONTHS_ES


class AccountMove(models.Model):
    _inherit = "account.move"

    def action_print_pdf(self):
        self.ensure_one()
        return self.env.ref("account.account_invoices").report_action(self.id, config=False)

    def _get_sale_receipt_date_text(self):
        self.ensure_one()
        sale_order = self._get_sale_receipt_sale_order()
        receipt_date = (
            self.fcr_receipt_date
            or (sale_order.fcr_receipt_date if sale_order else False)
            or self.invoice_date
            or fields.Date.context_today(self)
        )
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
        return "RECIBO DE VENTA"

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
        line = self._get_sale_receipt_primary_line()
        return line.name or line.product_id.display_name if line else ""

    def _get_sale_receipt_primary_line(self):
        self.ensure_one()
        lines = self.invoice_line_ids.filtered(
            lambda line: not line.display_type and line.product_id
        )
        lines = lines.filtered(lambda line: not (
            "is_downpayment" in line._fields and line.is_downpayment
        ))
        lines = lines.filtered(lambda line: not any(
            field_name in line.product_id.product_tmpl_id._fields
            and line.product_id.product_tmpl_id[field_name]
            for field_name in ("is_marbete", "is_first_registration", "is_co2")
        ))
        vehicle_lines = lines.filtered(
            lambda line: "vehicle_id" in line.product_id.product_tmpl_id._fields
            and line.product_id.product_tmpl_id.vehicle_id
        )
        return (vehicle_lines or lines)[:1]

    def _get_sale_receipt_total_cost(self):
        self.ensure_one()
        sale_order = self._get_sale_receipt_sale_order()
        if sale_order:
            return sale_order._get_sale_receipt_total_cost()
        line = self._get_sale_receipt_primary_line()
        return line.price_total if line else 0.0

    def _get_sale_receipt_history_records(self):
        self.ensure_one()
        sale_order = self._get_sale_receipt_sale_order()
        if sale_order:
            return sale_order._get_sale_receipt_history_records()
        return self.env["fcr.sale.receipt.history"].sudo().search(
            [("invoice_id", "=", self.id)], order="id",
        )

    def _get_latest_sale_receipt_history(self):
        self.ensure_one()
        History = self.env["fcr.sale.receipt.history"].sudo()
        sale_order = self._get_sale_receipt_sale_order()
        if sale_order:
            history = sale_order._get_sale_receipt_history_records()
            return history[-1:] if history else History
        invoice_history = History.search([("invoice_id", "=", self.id)], order="id desc", limit=1)
        if invoice_history:
            return invoice_history
        history = self._get_sale_receipt_history_records()
        return history[-1:] if history else History

    def _get_sale_receipt_paid_to_date(self):
        self.ensure_one()
        sale_order = self._get_sale_receipt_sale_order()
        if sale_order:
            return sale_order._get_sale_receipt_paid_to_date()
        history = self._get_sale_receipt_history_records()
        return sum(history.mapped("amount")) if history else self._get_sale_receipt_initial_payment_amount()

    def _migrate_legacy_sale_receipt(self):
        self.ensure_one()
        sale_order = self._get_sale_receipt_sale_order()
        if sale_order:
            if sale_order._get_sale_receipt_history_records():
                return
            amount = self._get_sale_receipt_initial_payment_amount()
            if amount <= 0:
                sale_order._migrate_legacy_sale_receipt()
                return
            receipt_date = (
                self.fcr_receipt_date
                or sale_order.fcr_receipt_date
                or self.invoice_date
                or fields.Date.context_today(self)
            )
            self.env["fcr.sale.receipt.history"].sudo().create({
                "sale_order_id": sale_order.id,
                "invoice_id": self.id,
                "receipt_date": receipt_date,
                "currency_id": sale_order.currency_id.id,
                "amount": amount,
                "exchange_rate": self.fcr_receipt_exchange_rate
                or sale_order.fcr_receipt_exchange_rate
                or sale_order._get_sale_receipt_exchange_rate()
                or 0.0,
            })
            return

        if self._get_sale_receipt_history_records():
            return
        amount = self._get_sale_receipt_initial_payment_amount()
        if amount <= 0:
            return
        self.env["fcr.sale.receipt.history"].sudo().create({
            "invoice_id": self.id,
            "receipt_date": self.fcr_receipt_date or self.invoice_date or fields.Date.context_today(self),
            "currency_id": self.currency_id.id,
            "amount": amount,
            "exchange_rate": self.fcr_receipt_exchange_rate or self._get_sale_receipt_exchange_rate() or 0.0,
        })

    def _get_sale_receipt_exchange_rate(self):
        self.ensure_one()
        sale_order = self._get_sale_receipt_sale_order()
        if self.fcr_receipt_exchange_rate:
            return self.fcr_receipt_exchange_rate
        if sale_order and sale_order.fcr_receipt_exchange_rate:
            return sale_order.fcr_receipt_exchange_rate
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

        if self.currency_id == self.company_currency_id:
            return ""

        rate = self._get_sale_receipt_exchange_rate()
        if rate:
            sale_order = self._get_sale_receipt_sale_order()
            receipt_date = (
                self.fcr_receipt_date
                or (sale_order.fcr_receipt_date if sale_order else False)
                or self.invoice_date
                or fields.Date.context_today(self)
            )
            return f"Tasa del {self._get_sale_receipt_date_text_for(receipt_date)}: {rate:.2f}"
        return ""

    def _get_sale_receipt_initial_payment_amount(self):
        self.ensure_one()
        sale_order = self._get_sale_receipt_sale_order()
        if self.fcr_receipt_amount:
            return self.fcr_receipt_amount
        if sale_order and sale_order.fcr_receipt_amount:
            return sale_order.fcr_receipt_amount
        return self.amount_total - self.amount_residual

    def _get_sale_receipt_values(self):
        self.ensure_one()
        sale_order = self._get_sale_receipt_sale_order()
        latest_receipt = self._get_latest_sale_receipt_history()
        if sale_order:
            values = sale_order._get_sale_receipt_values(receipt_history=latest_receipt)
            if self.invoice_user_id:
                values["executive"] = self.invoice_user_id.name
            return values

        partner = self.partner_id
        history = self._get_sale_receipt_history_records()
        paid_to_date = sum(history.mapped("amount")) if history else self._get_sale_receipt_initial_payment_amount()
        advance_payment = latest_receipt.amount if latest_receipt else paid_to_date
        paid_before_current = max(paid_to_date - advance_payment, 0.0)
        receipt_date = (
            latest_receipt.receipt_date
            if latest_receipt
            else self.fcr_receipt_date or self.invoice_date or fields.Date.context_today(self)
        )
        exchange_rate = (
            latest_receipt.exchange_rate
            if latest_receipt
            else self._get_sale_receipt_exchange_rate()
        )
        exchange_rate_text = ""
        if self.currency_id != self.company_currency_id and exchange_rate:
            exchange_rate_text = (
                f"Tasa del {self._get_sale_receipt_date_text_for(receipt_date)}: {exchange_rate:.2f}"
            )
        total_cost = self._get_sale_receipt_total_cost()
        phone = partner.phone or ""
        if not phone and "mobile" in partner._fields:
            phone = partner.mobile or ""
        executive = self.invoice_user_id.name if self.invoice_user_id else ""
        if not executive and "user_id" in self._fields and self.user_id:
            executive = self.user_id.name

        return {
            "date_text": self._get_sale_receipt_date_text_for(receipt_date),
            "document_label": self._get_sale_receipt_document_label(),
            "company": self.company_id,
            "client": partner.name or "",
            "vat": partner.vat or "",
            "phone": phone,
            "email": partner.email or "",
            "vehicle": self._get_sale_receipt_vehicle(),
            "items_text": self._get_sale_receipt_items_text(),
            "initial_payment": advance_payment,
            "advance_payment": advance_payment,
            "paid_before_current": paid_before_current,
            "paid_to_date": paid_to_date,
            "total_cost": total_cost,
            "balance": max(total_cost - paid_to_date, 0.0),
            "currency": self.currency_id,
            "exchange_rate": exchange_rate,
            "exchange_rate_text": exchange_rate_text,
            "executive": executive,
        }
