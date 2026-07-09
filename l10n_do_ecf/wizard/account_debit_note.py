from odoo import models, fields, api, _


class AccountDebitNote(models.TransientModel):
    _inherit = "account.debit.note"

    def _prepare_default_values(self, move):
        res = super(AccountDebitNote, self)._prepare_default_values(move)

        # Include additional info when l10n_do debit note
        if self.country_code == "DO" and move.l10n_latam_use_documents:
            res.update(
                dict(
                    l10n_do_ecf_date_modification=move.invoice_date,
                )
            )

        return res
