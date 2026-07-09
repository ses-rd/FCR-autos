# -*- coding: utf-8 -*-
from odoo import models
from odoo.addons.account.models.chart_template import template


class AccountChartTemplate(models.AbstractModel):
    _inherit = 'account.chart.template'

    @template('do', 'account.tax')
    def _get_do_edi_account_tax(self):
        return self._parse_csv('do', 'account.tax', module='l10n_do_ecf')

    @template('do', 'account.tax.group')
    def _get_do_edi_account_tax_group(self):
        return self._parse_csv('do', 'account.tax.group', module='l10n_do_ecf')
