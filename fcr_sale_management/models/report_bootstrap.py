# -*- coding: utf-8 -*-

import logging

from odoo import api, models

_logger = logging.getLogger(__name__)


class IrActionsReport(models.Model):
    _inherit = "ir.actions.report"

    @api.model
    def _register_hook(self):
        result = super()._register_hook()
        try:
            self._fcr_ensure_receipt_report_data()
        except Exception:
            _logger.exception("Unable to bootstrap the FCR receipt report data.")
        return result

    @api.model
    def _fcr_ensure_receipt_report_data(self):
        target_report_name = "fcr_sale_management.report_sale_separation_receipt"
        sale_report = self.env.ref("sale.action_report_saleorder", raise_if_not_found=False)
        receipt_template = self.env.ref(target_report_name, raise_if_not_found=False)
        if sale_report and receipt_template and sale_report.report_name == target_report_name:
            return

        from odoo.tools.convert import convert_file

        idref = {}
        try:
            convert_file(
                self.env,
                "fcr_sale_management",
                "views/sale_order_receipt_report.xml",
                idref,
                mode="update",
                noupdate=False,
                kind="data",
            )
        except TypeError:
            convert_file(
                self.env.cr,
                "fcr_sale_management",
                "views/sale_order_receipt_report.xml",
                idref,
                mode="update",
                noupdate=False,
                kind="data",
            )
