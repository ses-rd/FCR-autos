# -*- coding: utf-8 -*-

from odoo import _, api, fields, models
from odoo.exceptions import UserError


class FcrSaleReceiptWizard(models.TransientModel):
    _name = "fcr.sale.receipt.wizard"
    _description = "FCR sale receipt draft"

    source_model = fields.Selection(
        [
            ("sale.order", "Orden de venta"),
            ("account.move", "Factura"),
        ],
        readonly=True,
    )
    source_id = fields.Integer(readonly=True)
    currency_id = fields.Many2one(
        "res.currency",
        compute="_compute_currency_id",
        readonly=True,
    )
    amount = fields.Monetary(string="Importe", currency_field="currency_id", required=True)
    receipt_date = fields.Date(string="Fecha", required=True)
    exchange_rate = fields.Float(string="Tasa del dia")

    def _compute_currency_id(self):
        for wizard in self:
            document = wizard._get_receipt_document(raise_if_missing=False)
            wizard.currency_id = (
                document.currency_id
                if document
                else False
                or self.env.company.currency_id
            )

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            source_model, source_id = self._get_source_from_values(vals)
            vals["source_model"] = source_model
            vals["source_id"] = source_id
        return super().create(vals_list)

    @api.model
    def action_open_for_document(self, document):
        document.ensure_one()
        receipt_date = (
            document.fcr_receipt_date
            or getattr(document, "invoice_date", False)
            or fields.Date.to_date(getattr(document, "date_order", False))
            or fields.Date.context_today(self)
        )
        receipt_rate = getattr(document, "_get_sale_receipt_exchange_rate", lambda: 0.0)()
        wizard = self.create({
            "source_model": document._name,
            "source_id": document.id,
            "amount": document.fcr_receipt_amount
            or getattr(document, "amount_residual", 0.0)
            or document.amount_total,
            "receipt_date": receipt_date,
            "exchange_rate": document.fcr_receipt_exchange_rate or receipt_rate or 0.0,
        })
        view = self.env.ref("fcr_invoice_report.view_fcr_sale_receipt_wizard_form")
        return {
            "type": "ir.actions.act_window",
            "name": "Recibo FCR",
            "res_model": self._name,
            "res_id": wizard.id,
            "view_mode": "form",
            "view_id": view.id,
            "views": [(view.id, "form")],
            "target": "new",
            "context": {
                "active_model": document._name,
                "active_id": document.id,
            },
        }

    def _get_source_from_values(self, vals=None):
        vals = vals or {}
        source_model = vals.get("source_model") or self.env.context.get("default_source_model")
        source_id = vals.get("source_id") or self.env.context.get("default_source_id")

        if not source_model or not source_id:
            active_model = self.env.context.get("active_model")
            active_id = self.env.context.get("active_id")
            if active_model in ("sale.order", "account.move") and active_id:
                source_model = active_model
                source_id = active_id

        if source_model not in ("sale.order", "account.move") or not source_id:
            raise UserError(_("No se encontro el documento para imprimir el Recibo FCR."))
        return source_model, source_id

    def _get_receipt_document(self, raise_if_missing=True):
        self.ensure_one()
        source_model = self.source_model
        source_id = self.source_id
        if not source_model or not source_id:
            source_model, source_id = self._get_source_from_values()

        document = self.env[source_model].browse(source_id).exists()
        if not document and source_model == "account.move":
            document = self.env["sale.order"].browse(source_id).exists()
        if document:
            return document
        if raise_if_missing:
            raise UserError(_("No se encontro el documento para imprimir el Recibo FCR."))
        return self.env["sale.order"]

    def default_get(self, fields_list):
        result = super().default_get(fields_list)
        source_model, source_id = self._get_source_from_values()
        result["source_model"] = source_model
        result["source_id"] = source_id

        document = self.env[source_model].browse(source_id).exists()
        if document:
            residual = getattr(document, "amount_residual", 0.0)
            result.setdefault("amount", document.fcr_receipt_amount or residual or document.amount_total)
            result.setdefault(
                "receipt_date",
                document.fcr_receipt_date
                or getattr(document, "invoice_date", False)
                or fields.Date.to_date(getattr(document, "date_order", False))
                or fields.Date.context_today(self),
            )
            result.setdefault("exchange_rate", document.fcr_receipt_exchange_rate or document._get_sale_receipt_exchange_rate() or 0.0)
        return result

    def action_save_and_print(self):
        self.ensure_one()
        document = self._get_receipt_document()
        document.write({
            "fcr_receipt_amount": self.amount,
            "fcr_receipt_date": self.receipt_date,
            "fcr_receipt_exchange_rate": self.exchange_rate,
        })
        if document._name == "account.move":
            report = self.env.ref("fcr_invoice_report.action_report_invoice_separation_receipt")
        else:
            report = self.env.ref("fcr_invoice_report.action_report_sale_separation_receipt")
        action = report.with_context(close_on_report_download=True).report_action(document, config=False)
        action["close_on_report_download"] = True
        return action
