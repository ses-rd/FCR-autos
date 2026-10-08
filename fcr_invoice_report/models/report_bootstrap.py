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
        target_report_name = "fcr_invoice_report.report_sale_separation_receipt"
        sale_report = self.env.ref("sale.action_report_saleorder", raise_if_not_found=False)
        receipt_template = self.env.ref(target_report_name, raise_if_not_found=False)
        if sale_report and receipt_template and sale_report.report_name == target_report_name:
            _logger.info("FCR receipt report data is already active on sale.action_report_saleorder.")
            return

        _logger.warning(
            "FCR receipt report data is not active; loading receipt XML. "
            "sale_report=%s report_name=%s receipt_template=%s",
            bool(sale_report),
            sale_report.report_name if sale_report else "",
            bool(receipt_template),
        )
        from odoo.tools.convert import convert_file

        idref = {}
        try:
            convert_file(
                self.env,
                "fcr_invoice_report",
                "views/sale_order_receipt_report.xml",
                idref,
                mode="update",
                noupdate=False,
                kind="data",
            )
            _logger.info("FCR receipt report XML loaded using env convert_file signature.")
        except TypeError:
            convert_file(
                self.env.cr,
                "fcr_invoice_report",
                "views/sale_order_receipt_report.xml",
                idref,
                mode="update",
                noupdate=False,
                kind="data",
            )
            _logger.info("FCR receipt report XML loaded using cr convert_file signature.")

        sale_report = self.env.ref("sale.action_report_saleorder", raise_if_not_found=False)
        receipt_template = self.env.ref(target_report_name, raise_if_not_found=False)
        _logger.info(
            "FCR receipt report bootstrap result: sale_report=%s report_name=%s receipt_template=%s",
            bool(sale_report),
            sale_report.report_name if sale_report else "",
            bool(receipt_template),
        )
