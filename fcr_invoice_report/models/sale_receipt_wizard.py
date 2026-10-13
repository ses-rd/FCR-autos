# -*- coding: utf-8 -*-

from odoo import fields, models


class FcrSaleReceiptWizard(models.TransientModel):
    _name = "fcr.sale.receipt.wizard"
    _description = "FCR sale receipt draft"

    move_id = fields.Many2one("account.move", required=True, readonly=True)
    currency_id = fields.Many2one(related="move_id.currency_id", readonly=True)
    amount = fields.Monetary(string="Importe", currency_field="currency_id", required=True)
    receipt_date = fields.Date(string="Fecha", required=True)
    exchange_rate = fields.Float(string="Tasa del dia")

    def default_get(self, fields_list):
        result = super().default_get(fields_list)
        move = self.env["account.move"].browse(result.get("move_id") or self.env.context.get("default_move_id"))
        if move:
            result.setdefault("amount", move.fcr_receipt_amount or move.amount_residual or move.amount_total)
            result.setdefault("receipt_date", move.fcr_receipt_date or move.invoice_date or fields.Date.context_today(self))
            result.setdefault("exchange_rate", move.fcr_receipt_exchange_rate or move._get_sale_receipt_exchange_rate() or 0.0)
        return result

    def action_save_and_print(self):
        self.ensure_one()
        self.move_id.write({
            "fcr_receipt_amount": self.amount,
            "fcr_receipt_date": self.receipt_date,
            "fcr_receipt_exchange_rate": self.exchange_rate,
        })
        return self.env.ref("fcr_invoice_report.action_report_invoice_separation_receipt").report_action(
            self.move_id,
            config=False,
        )
