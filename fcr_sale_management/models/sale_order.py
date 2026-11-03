# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import UserError


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

    fcr_receipt_amount = fields.Monetary(
        string="Importe de recibo FCR",
        currency_field="currency_id",
        copy=False,
    )
    fcr_receipt_date = fields.Date(string="Fecha de recibo FCR", copy=False)
    fcr_receipt_exchange_rate = fields.Float(string="Tasa de recibo FCR", copy=False)

    def _get_order_lines_to_report(self):
        lines = super()._get_order_lines_to_report()
        return lines.filtered(
            lambda line: not (
                line.product_id
                and (
                    line.product_id.is_marbete
                    or line.product_id.is_first_registration
                    or line.product_id.is_co2
                )
            )
        )

    def _get_totals(self):
        for record in self:
            tax_totals = record.tax_totals
            totals = []

            if tax_totals.get('has_tax_groups', False):
                subtotals = tax_totals['subtotals']
                for subtotal in subtotals:
                    tax_groups = subtotal.get('tax_groups', [])
                    if not tax_groups:
                        continue

                    tax_group_do = self.env['account.tax.group'].search([('l10n_do_billing_indicator', 'in', ['taxable_itbis', 'taxable_isr', 'tips', 'other'])], order='sequence asc')

                    # for tax_group in tax_groups:
                    for tax_group in list(filter(lambda m: m['id'] in tax_group_do.ids, tax_groups)):
                        tax_group_id = tax_group.get('id')
                        involved_tax_ids = tax_group.get('involved_tax_ids', [])
                        tax = self.env['account.tax'].search([('id', 'in', involved_tax_ids), ('tax_group_id', '=', tax_group_id)], limit=1)

                        base_name = f"{tax.name}:"

                        totals.append({
                            'base_name': base_name,
                            'base_amount': tax_group.get('base_amount', 0.0),
                            'tax_amount': tax_group.get('tax_amount', 0.0)
                        })
            # totals.sort(key=lambda x: x.get('tax_amount', 0.0), reverse=True)
            return totals

    def _get_co2_totals(self):
        for record in self:
            other_totals = []
            co2_lines = record.order_line.filtered(
                lambda line: line.product_id and line.product_id.is_co2
            )
            if not co2_lines:
                return other_totals

            totals_by_product = {}
            for line in co2_lines:
                product_name = line.product_id.display_name or line.name
                amount = line.price_subtotal
                if line.product_id.id in totals_by_product:
                    totals_by_product[line.product_id.id]['other_amount'] += amount
                else:
                    totals_by_product[line.product_id.id] = {
                        'other_name': product_name,
                        'other_amount': amount,
                    }

            return list(totals_by_product.values())

    def _get_first_registration_totals(self):
        for record in self:
            other_totals = []
            first_lines = record.order_line.filtered(
                lambda line: line.product_id and line.product_id.is_first_registration
            )
            if not first_lines:
                return other_totals

            totals_by_product = {}
            for line in first_lines:
                product_name = line.product_id.display_name or line.name
                amount = line.price_subtotal
                if line.product_id.id in totals_by_product:
                    totals_by_product[line.product_id.id]['other_amount'] += amount
                else:
                    totals_by_product[line.product_id.id] = {
                        'other_name': product_name,
                        'other_amount': amount,
                    }

            return list(totals_by_product.values())

    def _get_marbete_totals(self):
        for record in self:
            other_totals = []
            marbete_lines = record.order_line.filtered(
                lambda line: line.product_id and line.product_id.is_marbete
            )
            if not marbete_lines:
                return other_totals

            totals_by_product = {}
            for line in marbete_lines:
                product_name = line.product_id.display_name or line.name
                amount = line.price_subtotal
                if line.product_id.id in totals_by_product:
                    totals_by_product[line.product_id.id]['other_amount'] += amount
                else:
                    totals_by_product[line.product_id.id] = {
                        'other_name': product_name,
                        'other_amount': amount,
                    }

            return list(totals_by_product.values())

    def _get_sale_receipt_date_text(self):
        self.ensure_one()
        receipt_date = self.fcr_receipt_date or fields.Date.context_today(self)
        if self.date_order:
            receipt_date = self.fcr_receipt_date or fields.Date.to_date(self.date_order)
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

        product_line = self._get_sale_receipt_primary_line()
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

    def _get_sale_receipt_primary_line(self):
        self.ensure_one()
        lines = self.order_line.filtered(
            lambda line: not line.display_type
            and line.product_id
            and not ("is_downpayment" in line._fields and line.is_downpayment)
        )
        lines = lines.filtered(lambda line: not any(
            field_name in line.product_id.product_tmpl_id._fields
            and line.product_id.product_tmpl_id[field_name]
            for field_name in ("is_marbete", "is_first_registration", "is_co2")
        ))
        vehicle_lines = lines.filtered(
            lambda line: "vehicle_id" in line.product_template_id._fields
            and line.product_template_id.vehicle_id
        )
        return (vehicle_lines or lines)[:1]

    def _get_sale_receipt_items_text(self):
        self.ensure_one()
        line = self._get_sale_receipt_primary_line()
        return line.name or line.product_id.display_name if line else ""

    def _get_sale_receipt_total_cost(self):
        self.ensure_one()
        line = self._get_sale_receipt_primary_line()
        return line.price_total if line else 0.0

    def _get_sale_receipt_paid_amount(self):
        self.ensure_one()
        if self.fcr_receipt_amount:
            return self.fcr_receipt_amount
        downpayment_lines = self.order_line.filtered(
            lambda line: not line.display_type and "is_downpayment" in line._fields and line.is_downpayment
        )
        return sum(downpayment_lines.mapped("price_total"))

    def _get_sale_receipt_history_records(self):
        self.ensure_one()
        return self.env["fcr.sale.receipt.history"].sudo().search(
            [("sale_order_id", "=", self.id)], order="id",
        )

    def _get_sale_receipt_paid_to_date(self):
        self.ensure_one()
        history = self._get_sale_receipt_history_records()
        return sum(history.mapped("amount")) if history else self._get_sale_receipt_paid_amount()

    def _migrate_legacy_sale_receipt(self):
        self.ensure_one()
        if self._get_sale_receipt_history_records():
            return
        amount = self._get_sale_receipt_paid_amount()
        if amount <= 0:
            return
        receipt_date = (
            self.fcr_receipt_date
            or fields.Date.to_date(self.date_order)
            or fields.Date.context_today(self)
        )
        self.env["fcr.sale.receipt.history"].sudo().create({
            "sale_order_id": self.id,
            "receipt_date": receipt_date,
            "currency_id": self.currency_id.id,
            "amount": amount,
            "exchange_rate": self.fcr_receipt_exchange_rate or self._get_sale_receipt_exchange_rate() or 0.0,
        })

    def _get_sale_receipt_exchange_rate(self):
        self.ensure_one()
        if self.fcr_receipt_exchange_rate:
            return self.fcr_receipt_exchange_rate
        if "manual_currency_exchange_rate" in self._fields and self.manual_currency_exchange_rate:
            return self.manual_currency_exchange_rate
        if "currency_rate" in self._fields and self.currency_rate:
            return self.currency_rate
        return ""

    def _get_sale_receipt_exchange_rate_text(self):
        self.ensure_one()
        if self.currency_id == self.company_id.currency_id:
            return ""
        rate = self._get_sale_receipt_exchange_rate()
        if rate:
            receipt_date = self.fcr_receipt_date or self.date_order or fields.Date.context_today(self)
            return f"Tasa del {self._get_sale_receipt_date_text_for(receipt_date)}: {rate:.2f}"
        return ""

    def _get_sale_receipt_document_label(self):
        self.ensure_one()
        return "RECIBO DE VENTA"

    def action_print_sale_separation_receipt(self):
        self.ensure_one()
        if self.state not in ("sale", "done"):
            raise UserError(_("El Recibo FCR solo esta disponible en ordenes de venta confirmadas."))
        return self.env["fcr.sale.receipt.wizard"].action_open_for_document(self)

    def _get_sale_receipt_values(self, receipt_history=None):
        self.ensure_one()
        partner = self.partner_id
        history = self._get_sale_receipt_history_records()
        latest_receipt = receipt_history or (history[-1:] if history else self.env["fcr.sale.receipt.history"])
        paid_to_date = sum(history.mapped("amount")) if history else self._get_sale_receipt_paid_amount()
        advance_payment = latest_receipt.amount if latest_receipt else paid_to_date
        paid_before_current = max(paid_to_date - advance_payment, 0.0)
        receipt_date = (
            latest_receipt.receipt_date
            if latest_receipt
            else self.fcr_receipt_date or fields.Date.to_date(self.date_order) or fields.Date.context_today(self)
        )
        exchange_rate = (
            latest_receipt.exchange_rate
            if latest_receipt
            else self._get_sale_receipt_exchange_rate()
        )
        exchange_rate_text = ""
        if self.currency_id != self.company_id.currency_id and exchange_rate:
            exchange_rate_text = (
                f"Tasa del {self._get_sale_receipt_date_text_for(receipt_date)}: {exchange_rate:.2f}"
            )
        total_cost = self._get_sale_receipt_total_cost()
        phone = partner.phone or ""
        if not phone and "mobile" in partner._fields:
            phone = partner.mobile or ""

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
            "executive": self.user_id.name or "",
        }
