# -*- coding: utf-8 -*-
from odoo import models, fields, api


class SalesOrder(models.Model):
    _inherit = 'sale.order'

    manual_currency_exchange_rate = fields.Float(string='Manual Currency Exchange Rate')

    def _prepare_invoice(self):
        result = super(SalesOrder, self)._prepare_invoice()
        result.update({
            'manual_currency_exchange_rate': self.manual_currency_exchange_rate,
        })

        return result
