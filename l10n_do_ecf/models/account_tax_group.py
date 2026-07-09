# -*- coding: utf-8 -*-
from odoo import _, api, fields, models


class AccountTaxGroup(models.Model):

    _inherit = 'account.tax.group'

    l10n_do_billing_indicator = fields.Selection([
        ('not_applicable', 'Not Applicable'),
        ('taxable_itbis', 'Taxable ITBIS'),
        ('taxable_isr', 'Taxable ISR'),
        ('exempt', 'Exempt'),
        ('tips', 'Tips'),
        ('other', 'Other'),
    ], string='Billing Indicator')
