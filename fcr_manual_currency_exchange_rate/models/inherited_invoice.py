# -*- coding: utf-8 -*-


from odoo import models, fields, api


class AccountMove(models.Model):
    _inherit = 'account.move'

    manual_currency_exchange_rate = fields.Float(string='Manual Currency Exchange Rate')
