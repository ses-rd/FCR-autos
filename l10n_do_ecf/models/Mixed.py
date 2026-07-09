# -*- coding: utf-8 -*-


class MixedLib:

    def __init__(self, document_id, ceconfig):
        self.document_id = document_id
        self.partner_id = document_id.partner_id
        self.invoice_id = self.document_id.invoice_id
        self.ceconfig = ceconfig

    @staticmethod
    def limit(text, limit):
        return (text[:limit - 3] + '...') if len(text) > limit else text
