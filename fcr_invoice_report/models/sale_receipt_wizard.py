# -*- coding: utf-8 -*-

from odoo import _, api, fields, models
from odoo.exceptions import UserError


class FcrSaleReceiptWizard(models.TransientModel):
    _name = "fcr.sale.receipt.wizard"
    _description = "FCR sale receipt draft"

    move_id = fields.Many2one("account.move", readonly=True)
    sale_order_id = fields.Many2one("sale.order", readonly=True)
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
            vals["sale_order_id"] = source_id if source_model == "sale.order" else False
            vals["move_id"] = source_id if source_model == "account.move" else False
        return super().create(vals_list)

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

        if not source_model or not source_id:
            sale_order_id = vals.get("sale_order_id") or self.env.context.get("default_sale_order_id")
            move_id = vals.get("move_id") or self.env.context.get("default_move_id")
            if sale_order_id:
                source_model = "sale.order"
                source_id = sale_order_id
            elif move_id:
                if self.env["account.move"].browse(move_id).exists():
                    source_model = "account.move"
                    source_id = move_id
                elif self.env["sale.order"].browse(move_id).exists():
                    source_model = "sale.order"
                    source_id = move_id

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
        default_move_id = self.env.context.get("default_move_id")
        default_sale_order_id = self.env.context.get("default_sale_order_id")
        source_model, source_id = self._get_source_from_values({
            "sale_order_id": default_sale_order_id,
            "move_id": default_move_id,
        })
        result["source_model"] = source_model
        result["source_id"] = source_id
        result["sale_order_id"] = source_id if source_model == "sale.order" else False
        result["move_id"] = source_id if source_model == "account.move" else False

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
