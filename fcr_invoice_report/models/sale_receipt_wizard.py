# -*- coding: utf-8 -*-

from odoo import fields, models


class FcrSaleReceiptWizard(models.TransientModel):
    _name = "fcr.sale.receipt.wizard"
    _description = "FCR sale receipt draft"

    move_id = fields.Many2one("account.move", readonly=True)
    sale_order_id = fields.Many2one("sale.order", readonly=True)
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
            wizard.currency_id = (
                wizard.move_id.currency_id
                or wizard.sale_order_id.currency_id
                or self.env.company.currency_id
            )

    def _get_receipt_document(self):
        self.ensure_one()
        return self.move_id or self.sale_order_id

    def default_get(self, fields_list):
        result = super().default_get(fields_list)
        move = self.env["account.move"].browse(result.get("move_id") or self.env.context.get("default_move_id"))
        sale_order = self.env["sale.order"].browse(
            result.get("sale_order_id") or self.env.context.get("default_sale_order_id")
        )
        document = move or sale_order
        if document:
            residual = getattr(document, "amount_residual", 0.0)
            result.setdefault("amount", document.fcr_receipt_amount or residual or document.amount_total)
            result.setdefault(
                "receipt_date",
                document.fcr_receipt_date
                or getattr(document, "invoice_date", False)
                or fields.Date.to_date(getattr(document, "date_order", False))
                or fields.Date.context_today(self),
            )
            result.setdefault("exchange_rate", document.fcr_receipt_exchange_rate or document._get_sale_receipt_exchange_rate() or 0.0)
        return result

    def action_save_and_print(self):
        self.ensure_one()
        document = self._get_receipt_document()
        document.write({
            "fcr_receipt_amount": self.amount,
            "fcr_receipt_date": self.receipt_date,
            "fcr_receipt_exchange_rate": self.exchange_rate,
        })
        if self.move_id:
            report = self.env.ref("fcr_invoice_report.action_report_invoice_separation_receipt")
        else:
            report = self.env.ref("fcr_invoice_report.action_report_sale_separation_receipt")
        return report.report_action(document, config=False)
