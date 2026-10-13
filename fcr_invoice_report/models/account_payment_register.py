# -*- coding: utf-8 -*-

from odoo import models


class AccountPaymentRegister(models.TransientModel):
    _inherit = "account.payment.register"

    def default_get(self, fields_list):
        result = super().default_get(fields_list)
        if "amount" not in fields_list:
            return result

        if self.env.context.get("active_model") != "account.move":
            return result

        moves = self.env["account.move"].browse(self.env.context.get("active_ids") or [])
        if len(moves) != 1:
            return result

        move = moves[0]
        if move.move_type not in ("out_invoice", "out_receipt") or not move.fcr_receipt_amount:
            sale_order = move._get_sale_receipt_sale_order()
            if not sale_order or not sale_order.fcr_receipt_amount:
                return result
            result["amount"] = min(sale_order.fcr_receipt_amount, move.amount_residual or sale_order.fcr_receipt_amount)
            return result

        result["amount"] = min(move.fcr_receipt_amount, move.amount_residual or move.fcr_receipt_amount)
        return result
