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
        receipt_template = self.env.ref(target_report_name, raise_if_not_found=False)
        receipt_action = self.env.ref(
            "fcr_invoice_report.action_report_sale_separation_receipt",
            raise_if_not_found=False,
        )
        if not receipt_template or not receipt_action:
            _logger.warning(
                "FCR receipt report action/template is missing; loading receipt XML. "
                "receipt_action=%s receipt_template=%s",
                bool(receipt_action),
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

        self._fcr_restore_standard_report_defaults()

    @api.model
    def _fcr_restore_standard_report_defaults(self):
        sale_report = self.env.ref("sale.action_report_saleorder", raise_if_not_found=False)
        if sale_report:
            sale_report.write({
                "name": "Quotation / Order",
                "report_name": "sale.report_saleorder",
                "report_file": "sale.report_saleorder",
                "print_report_name": "(object.state in ('draft', 'sent') and 'Quotation - %s' % (object.name)) or 'Order - %s' % (object.name)",
                "paperformat_id": False,
            })

        invoice_report = self.env.ref("account.account_invoices", raise_if_not_found=False)
        if invoice_report:
            invoice_report.write({
                "name": "Invoices",
                "report_name": "account.report_invoice_with_payments",
                "report_file": "account.report_invoice_with_payments",
                "print_report_name": "(object._get_report_base_filename())",
                "paperformat_id": False,
            })

        invoice_without_payment = self.env.ref("account.account_invoices_without_payment", raise_if_not_found=False)
        if invoice_without_payment:
            invoice_without_payment.write({
                "name": "Invoices without Payment",
                "report_name": "account.report_invoice",
                "report_file": "account.report_invoice",
                "print_report_name": "(object._get_report_base_filename())",
                "paperformat_id": False,
            })

        receipt_action = self.env.ref(
            "fcr_invoice_report.action_report_sale_separation_receipt",
            raise_if_not_found=False,
        )
        if receipt_action:
            receipt_action.write({
                "binding_model_id": False,
                "binding_type": False,
            })

        _logger.info(
            "FCR receipt report is available as a button; standard defaults restored. "
            "sale_report=%s report_name=%s receipt_action=%s",
            bool(sale_report),
            sale_report.report_name if sale_report else "",
            bool(receipt_action),
        )
