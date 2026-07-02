# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.addons.l10n_do_ecf.models.account_move import PAYMENT_METHOD_SELECTION


class SaleOrder(models.Model):
    _inherit = "sale.order"

    l10n_do_ecf_payment_method = fields.Selection(PAYMENT_METHOD_SELECTION, string="e-CF Payment Method",
                                                  compute="_compute_l10n_do_payment_method_id", store=True,
                                                  readonly=False)

    @api.depends("partner_id")
    def _compute_l10n_do_payment_method_id(self):
        default_payment_method_id = "0"
        for order in self:
            if order.country_code == 'DO':
                order.l10n_do_ecf_payment_method = (
                        order.partner_id.l10n_do_ecf_payment_method or
                        order.l10n_do_ecf_payment_method or
                        default_payment_method_id
                )
            else:
                order.l10n_do_ecf_payment_method = False

    def _prepare_invoice(self):
        # EXTENDS 'sale'
        self.ensure_one()
        vals = super()._prepare_invoice()
        if self.country_code != 'DO':
            return vals

        vals['l10n_do_ecf_payment_method'] = self.l10n_do_ecf_payment_method
        return vals
