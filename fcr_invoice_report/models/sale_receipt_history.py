# -*- coding: utf-8 -*-

from odoo import fields, models


class FcrSaleReceiptHistory(models.Model):
    _name = "fcr.sale.receipt.history"
    _description = "FCR sale receipt payment history"
    _order = "id"
    _rec_name = "name"

    name = fields.Char(required=True, default="Recibo FCR")
    sale_order_id = fields.Many2one("sale.order", index=True, ondelete="cascade")
    invoice_id = fields.Many2one("account.move", index=True, ondelete="cascade")
    receipt_date = fields.Date(required=True)
    currency_id = fields.Many2one("res.currency", required=True)
    amount = fields.Monetary(required=True, currency_field="currency_id")
    exchange_rate = fields.Float()
