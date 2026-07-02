# -*- coding: utf-8 -*-
from . import models
from . import wizard


def _l10n_do_edi_post_init(env):
    for company in env['res.company'].search([('chart_template', '=', 'do')]):
        Template = env['account.chart.template'].with_company(company)
        Template._load_data({'account.tax.group': Template._get_do_edi_account_tax_group()})
        Template._load_data({'account.tax': Template._get_do_edi_account_tax()})
