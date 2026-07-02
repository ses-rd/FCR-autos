# -*- coding: utf-8 -*-
from odoo import models, fields, api, _


class AccountTax(models.Model):
    _inherit = 'account.tax'

    _ecf_code_unique = models.Constraint(
        'unique(company_id, ecf_code)',
        "ECF Code and company must be unique",
    )

    ecf_code = fields.Char(string='Taxes Additional ECF Code', size=3)
