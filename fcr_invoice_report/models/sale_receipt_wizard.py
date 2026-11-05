# -*- coding: utf-8 -*-

from odoo import _, api, fields, models
from odoo.exceptions import UserError


class FcrSaleReceiptWizard(models.TransientModel):
    _name = "fcr.sale.receipt.wizard"
    _description = "FCR sale receipt draft"

    sale_order_id = fields.Many2one("sale.order", readonly=True)
    move_id = fields.Many2one("account.move", readonly=True)
    currency_id = fields.Many2one(
        "res.currency",
        compute="_compute_currency_id",
        readonly=True,
    )
    amount = fields.Monetary(string="Importe", currency_field="currency_id", required=True)
    receipt_date = fields.Date(string="Fecha", required=True)
    exchange_rate = fields.Float(string="Tasa del dia")

    def _compute_currency_id(self):
        for wizard in self:
            document = wizard._get_receipt_document(raise_if_missing=False)
            wizard.currency_id = (
                document.currency_id
                if document
                else False
                or self.env.company.currency_id
            )

    @api.model
    def action_open_for_document(self, document):
        document.ensure_one()
        sale_order = self.env["sale.order"]
        move = self.env["account.move"]
        if document._name == "sale.order":
            sale_order = document
        elif document._name == "account.move" and document.move_type in ("out_invoice", "out_receipt"):
            move = document
            sale_order = document._get_sale_receipt_sale_order()
        else:
            raise UserError(_("Este asistente solo se puede abrir desde una orden de venta o factura de cliente."))

        receipt_source = sale_order or move
        receipt_date = (
            receipt_source.fcr_receipt_date
            or getattr(receipt_source, "invoice_date", False)
            or fields.Date.to_date(getattr(receipt_source, "date_order", False))
            or fields.Date.context_today(self)
        )
        receipt_rate = receipt_source._get_sale_receipt_exchange_rate()
        default_amount = (
            sale_order._get_sale_receipt_paid_amount()
            if sale_order
            else move._get_sale_receipt_initial_payment_amount()
        )
        if not default_amount and move:
            default_amount = move._get_sale_receipt_initial_payment_amount()
        wizard_values = {
            "sale_order_id": sale_order.id,
            "move_id": move.id,
            "amount": default_amount,
            "receipt_date": receipt_date,
            "exchange_rate": receipt_source.fcr_receipt_exchange_rate or receipt_rate or 0.0,
        }
        wizard = self.create(wizard_values)
        view = self.env.ref("fcr_invoice_report.view_fcr_sale_receipt_wizard_form")
        return {
            "type": "ir.actions.act_window",
            "name": "Recibo FCR",
            "res_model": self._name,
            "res_id": wizard.id,
            "view_mode": "form",
            "view_id": view.id,
            "views": [(view.id, "form")],
            "target": "new",
            "context": {
                "active_model": document._name,
                "active_id": document.id,
            },
        }

    def _get_receipt_document(self, raise_if_missing=True):
        self.ensure_one()
        document = self.sale_order_id.exists() or self.move_id.exists()
        if document:
            return document
        if raise_if_missing:
            raise UserError(_("No se encontro el documento para imprimir el Recibo FCR."))
        return self.env["sale.order"]

    def action_save_and_print(self):
        self.ensure_one()
        document = self._get_receipt_document()
        receipt_source = self.sale_order_id.exists() or self.move_id.exists()
        report_document = self.move_id.exists() or self.sale_order_id.exists()
        receipt_source.write({
            "fcr_receipt_amount": self.amount,
            "fcr_receipt_date": self.receipt_date,
            "fcr_receipt_exchange_rate": self.exchange_rate,
        })
        report_xmlid = (
            "fcr_invoice_report.action_report_invoice_separation_receipt"
            if self.move_id
            else "fcr_invoice_report.action_report_sale_separation_receipt"
        )
        report = self.env.ref(report_xmlid)
        action = report.with_context(close_on_report_download=True).report_action(report_document, config=False)
        action["close_on_report_download"] = True
        return action
