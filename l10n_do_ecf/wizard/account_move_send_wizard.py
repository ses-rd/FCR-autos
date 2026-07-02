# -*- coding: utf-8 -*-

from odoo import models


class AccountMoveSendWizard(models.TransientModel):
    _inherit = 'account.move.send.wizard'

    def action_send_and_print(self, allow_fallback_pdf=False):
        # EXTENDS account - to mark the CE state_mail as sent .

        res = super().action_send_and_print(allow_fallback_pdf=allow_fallback_pdf)
        if res:
            move = self.move_id
            if move.country_code in ['DO'] and move.l10n_latam_use_documents:
                if move.ecf_id and move.ecf_id.l10n_do_ecf_send_state in ['delivered_accepted', 'conditionally_accepted']:
                    move.ecf_id.state_mail = 'sent'
