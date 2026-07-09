from odoo import api, fields, models, Command


class L10nDoInvoiceRecreateWizard(models.Model):
    _name = 'l10n_do_ecf_invoice.recreate.wizard'
    _description = "Recreate Invoice Wizard"

    move_ids = fields.Many2many(comodel_name='account.move')

    @api.model
    def default_get(self, fields_list):
        # EXTENDS 'base'
        results = super().default_get(fields_list)

        if 'move_ids' in results:
            source_invoices = self.env['account.move'].browse(results['move_ids'][0][2])
            invoices = source_invoices._l10n_do_check_invoices_for_recreate()
            results['move_ids'] = [Command.set(invoices.ids)]

        return results

    def action_recreate_invoice(self):
        self.ensure_one()
        self.move_ids.l10n_do_ecf_invoice_retry_send()
