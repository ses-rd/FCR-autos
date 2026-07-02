# -*- coding: utf-8 -*-
from odoo import api, fields, models, _, Command
from odoo.exceptions import UserError
from lxml import etree
import logging

_logger = logging.getLogger(__name__)
parser = etree.XMLParser(remove_blank_text=True)

PAYMENT_METHOD_SELECTION = [
    ("0", "Not Defined"),
    ("1", "Cash"),
    ("2", "Bank"),
    ("3", "Card"),
    ("4", "Credit"),
    ("5", "Bond"),
    ("6", "Swap"),
    ("8", "Other"),
]


class AccountMove(models.Model):
    _inherit = "account.move"

    l10n_do_is_ecf_needed = fields.Boolean(
        compute='_compute_l10n_do_is_ecf_needed',
        store=True,
    )
    ecf_id = fields.Many2one('ecf.document', string='ECF Document', copy=False, readonly=True)
    l10n_do_ecf_payment_method = fields.Selection(PAYMENT_METHOD_SELECTION, string="e-CF Payment Method", default="0")
    is_rfce = fields.Boolean(related='ecf_id.is_rfce', string="Is RFCE")
    is_exportation = fields.Boolean(compute="_compute_is_exportation", store=True)
    l10n_do_ecf_send_state = fields.Selection(related='ecf_id.l10n_do_ecf_send_state', string='ECF Send State',
                                              tracking=True, store=True, copy=False, readonly=True)
    l10n_do_message_detail = fields.Text(string="Detalle del Mensaje", related="ecf_id.message_detail_dgii")
    l10n_do_ecf_security_code = fields.Char(string="e-CF Security Code", related="ecf_id.l10n_do_ecf_security_code")
    l10n_do_ecf_sign_date = fields.Char(string="e-CF Sign Date", related="ecf_id.l10n_do_ecf_sign_date")
    l10n_do_electronic_stamp = fields.Text(string="Electronic Stamp", related="ecf_id.l10n_do_electronic_stamp")
    l10n_do_ecf_date_modification = fields.Date(string="e-CF Date Modification")
    QR_code = fields.Binary(string="Code QR", related="ecf_id.QR_code")
    sequence_used = fields.Boolean(related="ecf_id.sequence_used", string="Sequence Used")
    customer_decision = fields.Selection(related="ecf_id.customer_decision", tracking=True)
    xml_amount_total = fields.Monetary('Amount Total')
    ecf_warning_message = fields.Html(readonly=True)

    # === COMPUTE METHODS ===#

    @api.depends("ecf_id")
    def _compute_is_exportation(self):
        for move in self:
            move.is_exportation = move.ecf_id and move.ecf_id.ncf_type == '46' or False

    @api.depends('move_type', 'company_currency_id', 'origin_payment_id', 'statement_line_id')
    def _compute_l10n_do_is_ecf_needed(self):
        """ Check whatever or not the ECF is needed on this invoice.
        """
        for move in self:
            move.l10n_do_is_ecf_needed = (
                    move._l10n_do_is_ecf_document()
            )

    # === BUSINESS METHODS ===#

    def _l10n_do_is_ecf_document(self):
        """ Helper to know if the current account.move is eligible for the DO ECF.

        :return: A boolean.
        """
        self.ensure_one()
        return (self.country_code == 'DO' and self.company_currency_id.name == 'DOP' and self.l10n_latam_use_documents
                and self.company_id.l10n_do_ecf_issuer)

    def _l10n_do_repare_document_vals(self):
        """ Set default value defined on the document .
        This method is called from the account.move when creating the document and may be overridden to implement custom

        Returns: A dict with the default values to create the ECF document.
        """

        ecf_vals = {
            'name': self.l10n_latam_document_number,
            'l10n_latam_document_type_id': self.l10n_latam_document_type_id.id,
            'invoice_id': self.id,
            'partner_id': self.partner_id.id,
            'currency_id': self.currency_id.id,
            'company_id': self.company_id.id,
        }
        if self.l10n_do_origin_ncf:
            ecf_vals.update({
                'l10n_do_origin_ncf': self.l10n_do_origin_ncf,
            })
        if self.l10n_do_ecf_modification_code:
            ecf_vals.update({
                'l10n_do_ecf_modification_code': self.l10n_do_ecf_modification_code,
            })

        return ecf_vals

    def _l10n_do_create_doc(self, recreate=False, remove=False):
        if remove:
            self.ecf_id.unlink()

        if not self.ecf_id or recreate:
            if recreate and not remove:
                document_number = self.l10n_do_fiscal_sequence_id.get_fiscal_number()
                self.write({"l10n_latam_document_number": document_number})
            ecf_vals = self._l10n_do_repare_document_vals()
            ecf_vals.update(self._l10n_do_prepare_document_additional_values())
            ce_id = self.env['ecf.document'].create(ecf_vals)
            self.write({'ecf_id': ce_id.id})
            return ce_id

    def l10n_do_recreate_document(self):
        if self.ecf_id and self.ecf_id.l10n_do_ecf_send_state == 'delivered_refused':
            """Sustituye factura rechazada por la DGII
               y hace referencia al documento actual rechazado"""

            company_id = self.company_id.id
            ref_doc_vals = {
                'name': 'Sustituye factura rechazada por DGII',
                'ref_number': self.ecf_id.name,
                'ref_date': self.ecf_id.create_date,
                'ref_reason': 'Sustituye factura rechazada por DGII',
                'company_id': company_id,
            }
            write_status = self._l10n_do_create_doc(recreate=True)
            if write_status:
                self.ecf_id.write({'ref_ids': [Command.create(ref_doc_vals)], "is_ref": True})

            return write_status

    def _l10n_do_prepare_document_additional_values(self):
        """
            Prepare the dict of values to create the additional values a documents. This method may be
            overridden to implement custom document generation (making sure to call super() to establish
            a clean extension chain).
            """
        self.ensure_one()
        return {

        }

    def _should_skip_move_for_ecf(self, move):
        """Determine if a move should be skipped for ECF processing.

        Returns:
            bool: True if the move should be skipped, False if it should be processed

        Skip scenarios:
        - Incoming invoices/refunds with specific NCF types (01-04, 31-32)
        - Incoming invoices without document type defined
        - Incoming refunds whose origin document is not a specific type
        """
        self.ensure_one()
        ncf_type = move.get_l10n_do_ncf_type()

        # Skip incoming documents with specific NCF types
        if move.move_type in ['in_invoice', 'in_refund'] and ncf_type in ["01", "02", "03", "04", "31", "32", "44"]:
            return True

        # Skip incoming invoices without document type
        if move.move_type in ['in_invoice', 'out_invoice'] and not move.l10n_latam_document_type_id.l10n_do_ncf_type:
            return True

        # Skip incoming refunds with non-eligible origin documents
        if move.move_type == "in_refund" and move.l10n_do_origin_ncf:
            credit_origin = self.env["account.move"].sudo().search(
                [("l10n_latam_document_number", "=", move.l10n_do_origin_ncf)],
                limit=1
            )
            if credit_origin.l10n_latam_document_type_id.l10n_do_ncf_type not in ["e-minor", "e-informal",
                                                                                  "e-exterior"]:
                return True

        return False

    def _post(self, soft=True):
        res = super(AccountMove, self)._post(soft)
        # Primero se llama al padre para q genere el consecutivos, establecer la fecha de vencimiento, etc.

        invoices = self._l10n_do_check_moves_for_send()
        for inv in invoices.filtered(lambda x: x.move_type not in ('entry',) and x.l10n_do_is_ecf_needed):
            inv.ecf_warning_message = ""
            # Skip moves that don't need ECF processing
            if self._should_skip_move_for_ecf(inv):
                continue

            if inv.partner_id and inv.l10n_latam_document_type_id:
                inv._check_invoice_type_document_type()
                try:
                    if not inv.ecf_id:
                        inv._l10n_do_create_doc()
                    elif inv.ecf_id and inv.ecf_id.l10n_do_ecf_send_state == 'delivered_refused':
                        inv.l10n_do_recreate_document()

                    ctx = self.env.context
                    propagate_is_modify = ctx.get("propagate_is_modify", False)
                    if not propagate_is_modify:  # When use "Revertir y crear fatura" en wizard NC.
                        inv.ecf_id.action_gen_xml()
                except Exception as e:
                    inv.ecf_warning_message = "No se pudo generar el XML: \n %s" % e

        return res

    def get_l10n_do_ncf_type(self):
        """
        Indicates if the document Code Type:

        31: Factura de Crédito Fiscal Electrónica
        32: Factura de Consumo Electrónica
        33: Nota de Débito Electrónica
        34: Nota de Crédito Electrónica
        41: Compras Electrónico
        43: Gastos Menores Electrónico
        44: Regímenes Especiales Electrónica
        45: Gubernamental Electrónico
        46: Comprobante para Exportaciones Electrónico
        47: Comprobante para Pagos al Exterior Electrónico
        """

        self.ensure_one()
        if not self.l10n_latam_document_type_id:
            return False

        return self.l10n_latam_document_type_id.doc_code_prefix[1:]

    def _get_report_base_filename(self):
        self.ensure_one()
        if self.l10n_do_is_ecf_needed and self.ecf_id:
            return self.ecf_id.name

        return super()._get_report_base_filename()

    def _l10n_do_check_moves_for_send(self):
        """ Ensure the current records are eligible for sent to DGII.

                """
        failed_moves = self.filtered(
            lambda o: o.l10n_do_is_ecf_needed and o.company_id.l10n_do_ecf_issuer and not (o.company_id._filter_ceconfig_by_company()))
        if failed_moves:
            invoices_str = ", ".join(failed_moves.mapped('name'))
            raise UserError(_("Invoices %s not selected an interface in a company.", invoices_str))

        invoices = self
        return invoices

    def l10n_do_invoice_recreate_wizard(self):
        """ Action to open the wizard allowing to recreate a document refused for the selected pos orders.

        :return: An action to open the wizard.
        """
        return {
            'name': _("Recreate Invoices"),
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'l10n_do_ecf_invoice.recreate.wizard',
            'target': 'new',
            'context': {'default_move_ids': [Command.set(self.ids)]},
        }

    def _l10n_do_check_invoices_for_recreate(self):
        failed_orders = self.filtered(lambda o: o.ecf_id and o.ecf_id.sequence_used)
        if failed_orders:
            invoices_str = ", ".join(failed_orders.mapped('l10n_latam_document_number'))
            raise UserError(_("Orders %s are not sequence_used.", invoices_str))

        invoices = self
        return invoices

    def l10n_do_ecf_invoice_retry_send(self):
        records_sorted = self.sorted('id')
        invoices = records_sorted._l10n_do_check_invoices_for_recreate()

        if len(invoices.company_id) != 1:
            raise UserError(_("You can only process orders sharing the same company."))

        for invoice in invoices:
            invoice._l10n_do_create_doc(remove=True)
            invoice.ecf_id.action_gen_xml()

    def _l10n_do_ecf_invoice_line_ids(self):
        """ Get the invoice lines to be considered when creating the ECF.

        :return: A recordset of invoice lines.
        """
        self.ensure_one()
        return self.invoice_line_ids.filtered(lambda line: (
            line.display_type == 'product'
            and not line.currency_id.is_zero(line.price_unit * line.quantity)
        ))

    # ===== BUTTONS =====

    def action_send_to_dgii(self):
        self.ensure_one()
        if self.state != 'posted':
            return

        invoices = self._l10n_do_check_moves_for_send()
        for move in invoices.filtered(lambda x: x.l10n_do_ecf_send_state in ['signed_pending', 'not_found']):
            move.ecf_id.action_send_to_dgii()

    def action_request_state_to_dgii(self):
        invoices = self._l10n_do_check_moves_for_send()
        for move in invoices.filtered(lambda x: x.l10n_do_ecf_send_state == 'delivered_pending'):
            move.ecf_id.action_request_state_to_dgii()

    def button_draft(self):
        if self.l10n_do_is_ecf_needed:
            if self.ecf_id and self._l10n_do_check_dgii_blocking_state():
                if not self._context.get("cancelled_by_dgii", False):
                    l10n_do_ecf_send_state = dict(self._fields['l10n_do_ecf_send_state']._description_selection(
                        self.env)).get(self.l10n_do_ecf_send_state)
                    raise UserError(_('This %s is in DGII status: %s. It cannot be cancelled. '
                                      'Instead you should revert it.') % (
                                        self.l10n_latam_document_type_id.name, l10n_do_ecf_send_state))
            elif self.ecf_id and self.l10n_do_ecf_send_state in ['to_send', 'signed_pending', 'not_found']:
                self.ecf_id.unlink()

        res = super(AccountMove, self).button_draft()
        return res

    def button_cancel(self):
        if self.l10n_do_is_ecf_needed:
            if self.ecf_id and self._l10n_do_check_dgii_blocking_state():
                if not self._context.get("cancelled_by_dgii", False):
                    l10n_do_ecf_send_state = dict(self._fields['l10n_do_ecf_send_state']._description_selection(
                        self.env)).get(self.l10n_do_ecf_send_state)
                    raise UserError(_('This %s is in DGII status: %s. It cannot be cancelled. '
                                      'Instead you should revert it.') % (
                                        self.l10n_latam_document_type_id.name, l10n_do_ecf_send_state))
            elif self.ecf_id and self.l10n_do_ecf_send_state in ['to_send', 'signed_pending', 'not_found']:
                self.ecf_id.unlink()

        res = super(AccountMove, self).button_cancel()
        return res

    def _l10n_do_check_dgii_blocking_state(self):
        """ Check if the invoice is in a blocking state for DGII.

        :return: True if the invoice is in a blocking state, False otherwise.
        """
        self.ensure_one()
        return self.l10n_do_ecf_send_state in ['delivered_accepted', 'conditionally_accepted',
                                               'delivered_pending']

    def action_recreate_xml(self):
        self.ecf_warning_message = ""
        self.l10n_do_ecf_invoice_retry_send()

