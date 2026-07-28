# -*- coding: utf-8 -*-

from odoo import models, api


class AccountMove(models.Model):
    _inherit = 'account.move'

    def _get_totals(self):
        for record in self:
            tax_totals = record.tax_totals
            totals = []

            if tax_totals.get('has_tax_groups', False):
                subtotals = tax_totals['subtotals']
                for subtotal in subtotals:
                    tax_groups = subtotal.get('tax_groups', [])
                    if not tax_groups:
                        continue

                    tax_group_iva13 = self.env['account.tax.group'].search([('l10n_do_billing_indicator', 'in', ['taxable_itbis', 'taxable_isr', 'tips', 'other'])])

                    # for tax_group in tax_groups:
                    for tax_group in list(filter(lambda m: m['id'] in tax_group_iva13.ids, tax_groups)):
                        tax_group_id = tax_group.get('id')
                        involved_tax_ids = tax_group.get('involved_tax_ids', [])
                        tax = self.env['account.tax'].search([('id', 'in', involved_tax_ids), ('tax_group_id', '=', tax_group_id)], limit=1)

                        # base_name = f"Gravado {int(tax.amount)}%:"
                        base_name = f"{tax.name}:"

                        totals.append({
                            'base_name': base_name,
                            'base_amount': tax_group.get('base_amount', 0.0),
                            'tax_amount': tax_group.get('tax_amount', 0.0)
                        })
            totals.sort(key=lambda x: x.get('tax_amount', 0.0), reverse=True)
            return totals

    # def _get_retention_totals(self):
    #     for record in self:
    #         tax_totals = record.tax_totals
    #         totals = {"base_name": "IVA Retenido:", "tax_amount": 0.0}
    #         if tax_totals.get('has_tax_groups', False):
    #             subtotals = tax_totals['subtotals']
    #             for subtotal in subtotals:
    #                 tax_groups = subtotal.get('tax_groups', [])
    #                 if not tax_groups:
    #                     continue
    #
    #                 tax_withholding1 = self.env['account.tax.group'].search(
    #                     [('l10n_sv_billing_indicator', '=', 'taxable')], limit=1)
    #                 tax_withholding13 = self.env['account.tax.group'].search(
    #                     [('l10n_sv_billing_indicator', '=', 'taxable13')], limit=1)
    #
    #                 # for tax_group in tax_groups:
    #                 for tax_group in list(filter(lambda m: m['id'] in [tax_withholding1.id, tax_withholding13.id], tax_groups)):
    #                     totals['tax_amount'] += abs(tax_group.get('tax_amount', 0.0))
    #
    #         return totals
