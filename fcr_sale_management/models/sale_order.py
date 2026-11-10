# -*- coding: utf-8 -*-
from odoo import api, fields, models


class SaleOrder(models.Model):
    _inherit = "sale.order"

    def _get_order_lines_to_report(self):
        lines = super()._get_order_lines_to_report()
        return lines.filtered(
            lambda line: not (
                line.product_id
                and (
                    line.product_id.is_marbete
                    or line.product_id.is_first_registration
                    or line.product_id.is_co2
                )
            )
        )

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

                    tax_group_do = self.env['account.tax.group'].search([('l10n_do_billing_indicator', 'in', ['taxable_itbis', 'taxable_isr', 'tips', 'other'])], order='sequence asc')

                    # for tax_group in tax_groups:
                    for tax_group in list(filter(lambda m: m['id'] in tax_group_do.ids, tax_groups)):
                        tax_group_id = tax_group.get('id')
                        involved_tax_ids = tax_group.get('involved_tax_ids', [])
                        tax = self.env['account.tax'].search([('id', 'in', involved_tax_ids), ('tax_group_id', '=', tax_group_id)], limit=1)

                        base_name = f"{tax.name}:"

                        totals.append({
                            'base_name': base_name,
                            'base_amount': tax_group.get('base_amount', 0.0),
                            'tax_amount': tax_group.get('tax_amount', 0.0)
                        })
            # totals.sort(key=lambda x: x.get('tax_amount', 0.0), reverse=True)
            return totals

    def _get_co2_totals(self):
        for record in self:
            other_totals = []
            co2_lines = record.order_line.filtered(
                lambda line: line.product_id and line.product_id.is_co2
            )
            if not co2_lines:
                return other_totals

            totals_by_product = {}
            for line in co2_lines:
                product_name = line.product_id.display_name or line.name
                amount = line.price_subtotal
                if line.product_id.id in totals_by_product:
                    totals_by_product[line.product_id.id]['other_amount'] += amount
                else:
                    totals_by_product[line.product_id.id] = {
                        'other_name': product_name,
                        'other_amount': amount,
                    }

            return list(totals_by_product.values())

    def _get_first_registration_totals(self):
        for record in self:
            other_totals = []
            first_lines = record.order_line.filtered(
                lambda line: line.product_id and line.product_id.is_first_registration
            )
            if not first_lines:
                return other_totals

            totals_by_product = {}
            for line in first_lines:
                product_name = line.product_id.display_name or line.name
                amount = line.price_subtotal
                if line.product_id.id in totals_by_product:
                    totals_by_product[line.product_id.id]['other_amount'] += amount
                else:
                    totals_by_product[line.product_id.id] = {
                        'other_name': product_name,
                        'other_amount': amount,
                    }

            return list(totals_by_product.values())

    def _get_marbete_totals(self):
        for record in self:
            other_totals = []
            marbete_lines = record.order_line.filtered(
                lambda line: line.product_id and line.product_id.is_marbete
            )
            if not marbete_lines:
                return other_totals

            totals_by_product = {}
            for line in marbete_lines:
                product_name = line.product_id.display_name or line.name
                amount = line.price_subtotal
                if line.product_id.id in totals_by_product:
                    totals_by_product[line.product_id.id]['other_amount'] += amount
                else:
                    totals_by_product[line.product_id.id] = {
                        'other_name': product_name,
                        'other_amount': amount,
                    }

            return list(totals_by_product.values())
