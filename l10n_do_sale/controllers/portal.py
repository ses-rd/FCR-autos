# -*- coding: utf-8 -*-

from odoo import http
from odoo.exceptions import AccessError, MissingError
from odoo.http import request

from odoo.addons.account.controllers.portal import PortalAccount


class FcrPortalAccount(PortalAccount):
    @http.route(['/my/invoices/<int:invoice_id>'], type='http', auth="public", website=True)
    def portal_my_invoice_detail(self, invoice_id, access_token=None, report_type=None, download=False, **kw):
        if report_type in ('html', 'pdf', 'text'):
            try:
                invoice_sudo = self._document_check_access('account.move', invoice_id, access_token)
            except (AccessError, MissingError):
                return request.redirect('/my')

            return self._show_report(
                model=invoice_sudo,
                report_type=report_type,
                report_ref='account.account_invoices',
                download=download,
            )

        return super().portal_my_invoice_detail(
            invoice_id,
            access_token=access_token,
            report_type=report_type,
            download=download,
            **kw
        )
