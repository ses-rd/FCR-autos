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
        if document._name not in ("sale.order", "account.move"):
            raise UserError(_("El Recibo FCR solo se puede imprimir desde una orden o factura."))
        receipt_date = (
            document.fcr_receipt_date
            or getattr(document, "invoice_date", False)
            or fields.Date.to_date(getattr(document, "date_order", False))
            or fields.Date.context_today(self)
        )
        receipt_rate = getattr(document, "_get_sale_receipt_exchange_rate", lambda: 0.0)()
        if document._name == "sale.order":
            default_amount = document._get_sale_receipt_paid_amount()
        else:
            default_amount = (
                document.fcr_receipt_amount
                or getattr(document, "amount_residual", 0.0)
                or document.amount_total
            )
        wizard_values = {
            "sale_order_id": document.id if document._name == "sale.order" else False,
            "move_id": document.id if document._name == "account.move" else False,
            "amount": default_amount,
            "receipt_date": receipt_date,
            "exchange_rate": document.fcr_receipt_exchange_rate or receipt_rate or 0.0,
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
        document.write({
            "fcr_receipt_amount": self.amount,
            "fcr_receipt_date": self.receipt_date,
            "fcr_receipt_exchange_rate": self.exchange_rate,
        })
        if document._name == "account.move":
            report = self.env.ref("fcr_invoice_report.action_report_invoice_separation_receipt")
        else:
            report = self.env.ref("fcr_invoice_report.action_report_sale_separation_receipt")
        action = report.with_context(close_on_report_download=True).report_action(document, config=False)
        action["close_on_report_download"] = True
        return action
