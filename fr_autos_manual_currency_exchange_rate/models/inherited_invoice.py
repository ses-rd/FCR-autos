# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) Sitaram Solutions (<https://sitaramsolutions.in/>).
#
#    For Module Support : info@sitaramsolutions.in  or Skype : contact.hiren1188
#
##############################################################################

from odoo import models, fields, api
from contextlib import contextmanager


class AccountMove(models.Model):
    _inherit = 'account.move'

    # apply_manual_currency_exchange = fields.Boolean(string='Apply Manual Currency Exchange')
    manual_currency_exchange_rate = fields.Float(string='Manual Currency Exchange Rate')
    # active_manual_currency_rate = fields.Boolean('active Manual Currency')

#     @api.onchange('company_id', 'currency_id')
#     def onchange_currency_id(self):
#         if self.company_id or self.currency_id:
#             if self.company_id.currency_id != self.currency_id:
#                 self.active_manual_currency_rate = True
#             else:
#                 self.active_manual_currency_rate = False
#         else:
#             self.active_manual_currency_rate = False
#
#     @api.depends('currency_id', 'company_currency_id', 'company_id', 'invoice_date', 'apply_manual_currency_exchange', 'manual_currency_exchange_rate')
#     def _compute_invoice_currency_rate(self):
#         for move in self:
#             if move.is_invoice(include_receipts=True):
#                 if move.currency_id:
#                     if move.apply_manual_currency_exchange:
#                         move.invoice_currency_rate = move.manual_currency_exchange_rate
#                     else:
#                         move.invoice_currency_rate = self.env['res.currency']._get_conversion_rate(
#                             from_currency=move.company_currency_id,
#                             to_currency=move.currency_id,
#                             company=move.company_id,
#                             date=move.invoice_date or fields.Date.context_today(move),
#                         )
#                 else:
#                     move.invoice_currency_rate = 1
#
#     @api.depends(
#         'line_ids.matched_debit_ids.debit_move_id.move_id.origin_payment_id.is_matched',
#         'line_ids.matched_debit_ids.debit_move_id.move_id.line_ids.amount_residual',
#         'line_ids.matched_debit_ids.debit_move_id.move_id.line_ids.amount_residual_currency',
#         'line_ids.matched_credit_ids.credit_move_id.move_id.origin_payment_id.is_matched',
#         'line_ids.matched_credit_ids.credit_move_id.move_id.line_ids.amount_residual',
#         'line_ids.matched_credit_ids.credit_move_id.move_id.line_ids.amount_residual_currency',
#         'line_ids.balance',
#         'line_ids.currency_id',
#         'line_ids.amount_currency',
#         'line_ids.amount_residual',
#         'line_ids.amount_residual_currency',
#         'line_ids.payment_id.state',
#         'line_ids.full_reconcile_id',
#         'state',
#         'apply_manual_currency_exchange',
#         'manual_currency_exchange_rate',
#         'active_manual_currency_rate')
#     def _compute_amount(self):
#         return super()._compute_amount()
#
#
# class AccountMoveLine(models.Model):
#     _inherit = 'account.move.line'
#
#     # New changes
#     @api.depends('currency_id', 'company_id', 'move_id.invoice_currency_rate', 'move_id.date', 'move_id.apply_manual_currency_exchange', 'move_id.manual_currency_exchange_rate')
#     def _compute_currency_rate(self):
#         for line in self:
#             if line.move_id.is_invoice(include_receipts=True):
#                 line.currency_rate = line.move_id.invoice_currency_rate
#             elif line.currency_id:
#                 if line.move_id.apply_manual_currency_exchange:
#                     line.currency_rate = line.move_id.manual_currency_exchange_rate
#                 else:
#                     line.currency_rate = self.env['res.currency']._get_conversion_rate(
#                         from_currency=line.company_currency_id,
#                         to_currency=line.currency_id,
#                         company=line.company_id,
#                         date=line._get_rate_date(),
#                     )
#             else:
#                 line.currency_rate = 1
#
#     @api.depends('product_id', 'product_uom_id', 'move_id.apply_manual_currency_exchange', 'move_id.manual_currency_exchange_rate')
#     def _compute_price_unit(self):
#         for line in self:
#             if not line.product_id or line.display_type in ('line_section', 'line_note') or line.is_imported:
#                 continue
#             if line.move_id.is_sale_document(include_receipts=True):
#                 document_type = 'sale'
#             elif line.move_id.is_purchase_document(include_receipts=True):
#                 document_type = 'purchase'
#             else:
#                 document_type = 'other'
#             if line.move_id.apply_manual_currency_exchange:
#                 line.price_unit = line.product_id.lst_price * line.move_id.manual_currency_exchange_rate
#             else:
#                 line.price_unit = line.product_id._get_tax_included_unit_price(
#                     line.move_id.company_id,
#                     line.move_id.currency_id,
#                     line.move_id.date,
#                     document_type,
#                     fiscal_position=line.move_id.fiscal_position_id,
#                     product_uom=line.product_uom_id,
#                 )
#
#     @contextmanager
#     def _sync_invoice(self, container):
#         if container['records'].env.context.get('skip_invoice_line_sync'):
#             yield
#             return  # avoid infinite recursion
#
#         def existing():
#             return {
#                 line: {
#                     'amount_currency': line.currency_id.round(line.amount_currency),
#                     'balance': line.company_id.currency_id.round(line.balance),
#                     'currency_rate': line.currency_rate,
#                     'price_subtotal': line.currency_id.round(line.price_subtotal),
#                     'move_type': line.move_id.move_type,
#                 } for line in container['records'].with_context(
#                     skip_invoice_line_sync=True,
#                 ).filtered(lambda l: l.move_id.is_invoice(True))
#             }
#
#         def changed(fname):
#             return line not in before or before[line][fname] != after[line][fname]
#
#         before = existing()
#         yield
#         after = existing()
#         protected = container.get('protected', {})
#         for line in after:
#             if (
#                 (changed('amount_currency') or changed('currency_rate') or changed('move_type'))
#                 and 'balance' not in protected.get(line, {})
#                 and (not changed('balance') or (line not in before and not line.balance))
#             ):
#                 if line.amount_currency and line.currency_rate:
#                     balance = line.company_id.currency_id.round(line.amount_currency / line.currency_rate)
#                 else:
#                     balance = 0
#                 line.balance = balance
#
#         self.env.add_to_compute(self._fields['debit'], container['records'])
#         self.env.add_to_compute(self._fields['credit'], container['records'])
