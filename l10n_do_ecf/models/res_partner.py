# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.addons.l10n_do_ecf.models.account_move import PAYMENT_METHOD_SELECTION


class ResPartner(models.Model):
    _inherit = "res.partner"

    l10n_do_ecf_payment_method = fields.Selection(PAYMENT_METHOD_SELECTION, string="e-CF Payment Method")
