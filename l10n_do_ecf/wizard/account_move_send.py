# -*- coding: utf-8 -*-

from odoo import models, fields, api


class AccountMoveSend(models.AbstractModel):
    _inherit = 'account.move.send'

    # -------------------------------------------------------------------------
    # ATTACHMENTS
    # -------------------------------------------------------------------------

    @api.model
    def _get_invoice_extra_attachments(self, move):
        """
                :returns: object (ir.attachment)
                """
        # EXTENDS 'account'

        # we require these to be downloadable for a better UX. It was also said that the xml and pdf files are
        # important files that needs to be shared with the customer.

        attachments = super()._get_invoice_extra_attachments(move)
        if move.country_code == 'DO' and move.l10n_latam_use_documents:
            if move.ecf_id and move.ecf_id.l10n_do_ecf_send_state in ['delivered_accepted', 'conditionally_accepted']:
                # Usar el método helper genérico de Document para obtener los adjuntos CR
                doc_attachments = move.ecf_id._get_do_document_attachments(
                    res_id=move.id,
                    res_model="account.move"
                )
                attachments |= doc_attachments

        return attachments
