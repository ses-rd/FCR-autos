# -*- coding: utf-8 -*-
from odoo import api, fields, models, _, Command
from odoo.exceptions import UserError, RedirectWarning, ValidationError
from datetime import datetime, timedelta
from odoo.fields import Domain
from . import E31
from . import libRFCE, RFCE
from . import E32
from . import E33
from . import E34
from . import E41
from . import E43
from . import E44
from . import E45
from . import E46
from . import E47
from odoo.tools import float_compare
from lxml import etree
from ..dgii_api import DGIIApi, DGII_VERSION
from collections import OrderedDict
from werkzeug import urls
import os
import re
import tempfile
import base64
import logging
import pyqrcode
import xml.etree.ElementTree as ET
import json
import xmltodict

_logger = logging.getLogger(__name__)
parser = etree.XMLParser(remove_blank_text=True)

ECF_STATE_MAP = {
    "Aceptado": "delivered_accepted",
    "Aceptado Condicional": "conditionally_accepted",
    "En Proceso": "delivered_pending",
    "Rechazado": "delivered_refused",
    "No encontrado": "not_found",
}

ECF_SEND_STATES = [("to_send", "Not sent"),
                   ("signed_pending", "Signed and pending"),
                   ("delivered_accepted", "Delivered and accepted"),
                   ("conditionally_accepted", "Conditionally accepted"),
                   ("delivered_pending", "Delivered and pending"),
                   ("delivered_refused", "Delivered and refused"),
                   ("not_found", "Not Found"),
                   ]

CUSTOMER_DECISION_STATES = [("pending", "Pending"),
                            ("accepted", "Accepted"),
                            ("system_accepted", "System Approved"),
                            ("reject", "Reject"),
                            ]

ACECF_SEND_STATES = [("pending", "Pending"),
                     ("accepted", "Accepted"),
                     ("reject", "Reject"),
                     ]

ECF_SEND_STATE_DESCRIPTIONS = (
    f"{ECF_SEND_STATES[0][1]}(Estado por defecto): ECF en borrador. En este punto aun no se ha construido el xml."
    f"\n {ECF_SEND_STATES[1][1]}: ECF firmado y pendiente de enviar a la DGII."    
    f"\n {ECF_SEND_STATES[2][1]}: ECF recepcionado y procesado de forma exitosa por la FGII."
    f"\n {ECF_SEND_STATES[3][1]}: ECF recepcionado y procesado, no cumplió en algún punto pero que no ameritó el rechazo."
    f"\n {ECF_SEND_STATES[4][1]}: ECF recepcionado y procesado, corresponde a que el comprobante aún no ha sido validado y por ende se debe esperar un tiempo prudencial antes de volver a consultar."
    f"\n {ECF_SEND_STATES[5][1]}: ECF recepcionado y procesado, implica la nulidad del comprobante para fines tributario debido a que en algún punto no cumplió."
    f"\n {ECF_SEND_STATES[6][1]}: No encontrado: Implica que no se encontró el trackid en los registros o que no se encontró el comprobante en los registros, pudiendo deberse a que aún no haya sido reportado."
)


class ECFDocument(models.Model):
    _name = 'ecf.document'
    _description = 'Electronic Document'
    _inherit = ["portal.mixin", "mail.thread", "mail.activity.mixin"]
    _order = "id desc"

    name = fields.Char(string='e-NCF', readonly=True, required=True)
    invoice_id = fields.Many2one('account.move', string='Invoice', ondelete='restrict', readonly=True,
                                 required=True, index=True)
    state = fields.Selection(
        selection=[
            ('invoice_sent', "Sent"),
            ('invoice_sent_failed', "Send In Error"),
            ('invoice_cancel', "Cancel"),
            ('invoice_cancel_failed', "Cancel In Error"),
        ],
        required=False,
    )
    l10n_latam_document_type_id = fields.Many2one('l10n_latam.document.type', string='Voucher Type', readonly=True)
    ncf_type = fields.Char(compute="_compute_ncf_type")
    is_rfce = fields.Boolean(compute="_compute_ncf_type", string="Is RFECF")
    l10n_do_ecf_send_state = fields.Selection(selection=ECF_SEND_STATES, string="e-CF Send State",
                                              copy=False, required=True, readonly=True, default="to_send",
                                              tracking=True, index=True,
                                              help=ECF_SEND_STATE_DESCRIPTIONS
                                              )
    company_id = fields.Many2one('res.company', string='Company', required=True)
    company_currency_id = fields.Many2one(
        string='Company Currency',
        related='company_id.currency_id', readonly=True,
    )
    partner_id = fields.Many2one('res.partner', string='Partner', readonly=True)
    xml_file = fields.Binary("XML File", attachment=True,
                             help="This field holds the XML file generated and signed by system")
    xml_file_name = fields.Char("Name of XML file")
    xml_rfce_file = fields.Binary("XML RFCE File", attachment=True,
                                  help="This field holds the XML file generated and signed by system")
    xml_rfce_file_name = fields.Char("Name of XML RFCE file")

    currency_id = fields.Many2one('res.currency', readonly=True, string='Currency')
    xml_amount_tax = fields.Float('Amount Total Tax')
    xml_amount_total = fields.Float('Amount Total')
    xml_amount_untaxed_signed = fields.Monetary('Amount Untaxed Signed', related="invoice_id.amount_untaxed_signed")
    xml_amount_total_signed = fields.Monetary('Amount Total Signed', related="invoice_id.amount_total_signed")
    sequence_used = fields.Boolean()
    l10n_do_origin_ncf = fields.Char(
        string="Modifies",
        copy=False,
        readonly=True,
    )
    l10n_do_ecf_modification_code = fields.Selection(
        string="e-CF Modification Code",
        selection=lambda self: self.env[
            "account.move"
        ]._get_l10n_do_ecf_modification_code(),
        copy=False,
        readonly=True,
    )

    # Response DGII
    xml_dgii_file = fields.Binary(string="XML DGII File", attachment=True, copy=False)
    xml_dgii_file_name = fields.Char(string="Nombre Archivo XML", copy=False)
    message_detail_dgii = fields.Text(string="Message Detail DGII", copy=False)
    response_status_code = fields.Text()

    # QR
    l10n_do_ecf_security_code = fields.Char(string="e-CF Security Code", copy=False, readonly=True)
    l10n_do_ecf_sign_date = fields.Char(string="e-CF Sign Date", copy=False, readonly=True)
    l10n_do_electronic_stamp = fields.Text(string="Electronic Stamp", copy=False, readonly=True)
    QR_code = fields.Binary(string="Code QR", readonly=True, copy=False)

    # Commercial Approved
    xml_commercial_approval_file = fields.Binary(attachment=True, string="Commercial Approval File",
                                                 help="This field holds the XML file generated and signed by system")
    xml_commercial_approval_file_name = fields.Char("Name of XML Commercial Approval File")
    xml_dgii_acecf_file = fields.Binary(string="XML ACECF DGII File", attachment=True, copy=False)
    xml_dgii_acecf_file_name = fields.Char(string="Nombre Archivo XML", copy=False)
    message_detail_dgii_acecf = fields.Text(string="Message Detail DGII ACECF", copy=False)
    customer_decision = fields.Selection(CUSTOMER_DECISION_STATES, default='pending')
    date_acknowledgment = fields.Datetime(readonly=True)
    l10n_do_acecf_send_state = fields.Selection(selection=ACECF_SEND_STATES, string="ACECF Send State",
                                                copy=False, readonly=True, default="pending")
    reject_reason = fields.Text()

    # Registry Information
    date_signed = fields.Datetime(readonly=True)

    # Mail
    state_mail = fields.Selection([('not_sent', 'Not Sent'),
                                   ('sent', 'Sent'),
                                   ('not_mail', 'Not Email')], string="State Email", default='not_sent', copy=False)

    # help to reference the current rejected document
    ref_ids = fields.Many2many('ecf.reference', string='Reference Documents')
    is_ref = fields.Boolean(default=False, help="Indicates whether the document is a substitute for a rejected invoice")

    # === COMPUTE METHODS ===#

    def _compute_ncf_type(self):
        for record in self:
            l10n_do_ncf_type = record.get_l10n_do_ncf_type()
            record.ncf_type = l10n_do_ncf_type
            record.is_rfce = l10n_do_ncf_type == '32' and record.xml_amount_untaxed_signed < 250000.00 or False

    # ===== BUTTONS =====

    def action_gen_xml(self):
        self.ensure_one()
        if self.xml_file:
            raise ValidationError(_('Error XML file already generated and cannot be modified'))

        # if len(self.invoice_id.invoice_line_ids) == 0 or abs(self.xml_amount_untaxed_signed) == 0.00:
        #     # Order is amount == 0 and no lines in it,
        #     # let's not create an XML for it
        #     return False

        ceconfig = self.company_id._filter_ceconfig_by_company()
        if not ceconfig:
            action = self.env.ref("base.action_res_company_form")
            msg = _("Must be selected an Environment in a Company.")
            raise RedirectWarning(msg, action.id, _("Go to Setting"))

        cedoc = self._gen_cedoc()
        if not cedoc:
            return
        now = fields.Datetime.context_timestamp(
            self.with_context(tz="America/Santo_Domingo"),
            fields.Datetime.now(),
        ).strftime("%d-%m-%Y %H:%M:%S")
        cedoc.set_FechaHoraFirma(now)
        file = tempfile.NamedTemporaryFile(delete=False)
        file.write(b'<?xml version="1.0" encoding="utf-8"?>')
        cedoc.export(file, 0, namespacedef_="", pretty_print=False)
        file.write(b'\n')
        file.close()

        res = self.sign_doc(file.name)
        if res and self.is_rfce:
            self._gen_xml_rfce()

        return res

    def action_send_to_dgii(self):
        documents = self._l10n_do_check_documents_for_send()
        for document in documents.filtered(lambda x: x.l10n_do_ecf_send_state in ['signed_pending', 'not_found']):
            document._send_to_dgii()

    def action_request_state_to_dgii(self):
        documents = self._l10n_do_check_documents_for_send()
        for document in documents.filtered(lambda x: x.l10n_do_ecf_send_state in ['delivered_pending']):
            document._action_update_state_to_dgii()

    def action_consultatrackids(self):
        ceconfig = self.company_id._filter_ceconfig_by_company()
        if not ceconfig:
            action = self.env.ref("base.action_res_company_form")
            msg = _("Must be selected an Environment in a Company.")
            raise RedirectWarning(msg, action.id, _("Go to Setting"))

        env = ceconfig.environment
        if env == 'CerteCF':
            raise UserError(_("This service is not available in this environment (%s)") % env)

        dgii_api = DGIIApi(ceconfig)
        response, vals = dgii_api.send_consultatrackids(self.company_id.vat, self.name)
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'type': 'info',
                'sticky': True,
                'message': "%s" % vals,
            }
        }

    def action_consultaestado(self):
        ceconfig = self.company_id._filter_ceconfig_by_company()
        if not ceconfig:
            action = self.env.ref("base.action_res_company_form")
            msg = _("Must be selected an Environment in a Company.")
            raise RedirectWarning(msg, action.id, _("Go to Setting"))

        dgii_api = DGIIApi(ceconfig)
        kernel = dgii_api.get_token_semilla()
        if not isinstance(kernel, dict):
            _logger.warning("Token inválido para la empresa '%s': %s", self.company_id.name, kernel)
            return False

        security_code = self.get_security_code()
        response, vals = dgii_api.send_ecf_status_request(
            rncemisor=self.company_id.vat, ncfelectronico=self.name, rnccomprador=self.partner_id.vat,
            codigoseguridad=security_code
        )
        if response.status_code == 200:
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'type': 'info',
                    'sticky': True,
                    'message': "%s" % vals,
                }
            }

    def action_send_mail(self):
        self._send_mail()

    # === BUSINESS METHODS ===#

    def gen_sender(self, classdoc):
        """Retorna la instancia de un emisor

            :param object classdoc: Clase del tipo de documento.
            :return: object Emisor del tipo de documento.
            """

        if self.ncf_type == '43':
            partner_id = self.partner_id
        else:
            partner_id = self.company_id.partner_id

        required_fields = self.env["ecf.document"]._l10n_do_validate_partner(partner_id)
        if required_fields:
            raise ValidationError(
                _("The selected company has missing required fields:\n%s", "\n".join(required_fields))
            )

        if not self.company_id.street or not len(str(self.company_id.street).strip()):
            # action = self.env.ref("base.action_res_company_form")
            msg = _('Your company has not defined a street.')
            raise UserError(msg)
            # raise RedirectWarning(msg, action.id, _("Go to Companies"))

        invoice_date = self.invoice_id.invoice_date
        if self.company_id.l10n_do_dgii_start_date and invoice_date < self.company_id.l10n_do_dgii_start_date:
            raise ValidationError(
                "La Fecha de Emision no puede ser menor a la Fecha de Inicio de Actividades de la compañia.")

        sender = classdoc.Emisor(RNCEmisor=self.company_id.vat,
                                 RazonSocialEmisor=self.limit(self.company_id.name, 150),
                                 DireccionEmisor=self.limit(self.company_id.street, 100),
                                 FechaEmision=invoice_date or fields.Date.today(),
                                 )

        if self.company_id.commercial_name:
            sender.set_NombreComercial(self.limit(self.company_id.commercial_name, 150))
        if partner_id.res_municipality_id:
            sender.set_Municipio(partner_id.res_municipality_id.ecf_code)
        if partner_id.state_id:
            sender.set_Provincia(partner_id.state_id.ecf_code)

        if not self.company_id.email:
            raise ValidationError(_('Your company has not defined an email which is mandatory'))

        if len(self.company_id.email) > 80:
            raise ValidationError("El correo de la empresa excede del Largo maximo %s" % 80)

        sender.set_CorreoEmisor(self.company_id.email)

        if self.company_id.website:
            website = self.company_id.website
            website_replace = website.replace("http://", "").replace("https://", "")
            if len(website_replace) > 50:
                raise ValidationError("El sitio web de la empresa excede del Largo maximo %s" % 50)
            sender.set_WebSite(website_replace)

        tabla_tel_emisor = classdoc.TablaTelefonoEmisor()
        if self.company_id.phone:
            phone = self.company_id.phone
            if re.match(r"^\d{3}-\d{3}-\d{4}$", phone):
                tabla_tel_emisor.add_TelefonoEmisor(self.company_id.phone)
            else:
                raise ValidationError(_('The company phone number must be in the format XXX-XXX-XXXX, where X is a digit.'))

        if tabla_tel_emisor.get_TelefonoEmisor():
            sender.set_TablaTelefonoEmisor(tabla_tel_emisor)

        return sender

    def gen_totals(self, classdoc):
        """Invoice amounts related values.

            :param object classdoc: Clase del tipo de documento.
            :return: object Total del tipo de documento.
            """
        self.ensure_one()
        self.xml_amount_tax = self.invoice_id.amount_tax
        self.xml_amount_total = self.invoice_id.amount_total
        l10n_do_ncf_type = self.ncf_type
        tax_data = self.get_taxed_amount_data()
        total_taxed = sum(
            [
                tax_data["18_taxed_base"],
                tax_data["16_taxed_base"],
                tax_data["0_taxed_base"],
            ]
        )
        total_itbis = sum(
            [
                tax_data["18_taxed_amount"],
                tax_data["16_taxed_amount"],
                tax_data["0_taxed_amount"],
            ]
        )

        currency = self.currency_id
        rate = 1
        is_company_currency = self.is_company_currency()
        if not is_company_currency:
            rate = abs(
                round(1 / (self.invoice_id.amount_total / (self.invoice_id.amount_total_signed or 1) or 1), 4)
            )

        totals = classdoc.Totales(MontoTotal=abs(currency.round(self.invoice_id.amount_untaxed) * rate))

        # Calculate net ITBIS after withholdings
        itbis_withholding_amount = abs(currency.round(tax_data["itbis_withholding_amount"]) * rate)
        net_itbis_18 = tax_data["18_taxed_amount"] + tax_data["itbis_withholding_amount"] if tax_data["itbis_withholding_amount"] else tax_data["18_taxed_amount"]
        net_itbis_16 = tax_data["16_taxed_amount"] + tax_data["itbis_withholding_amount"] if tax_data["itbis_withholding_amount"] else tax_data["16_taxed_amount"]
        net_total_itbis = total_itbis + tax_data["itbis_withholding_amount"] if tax_data["itbis_withholding_amount"] else total_itbis

        if l10n_do_ncf_type not in ("43", "44", "47"):
            if total_taxed:
                totals.set_MontoGravadoTotal(abs(currency.round(total_taxed) * rate))
            if tax_data["18_taxed_base"] and l10n_do_ncf_type != '46':
                totals.set_MontoGravadoI1(abs(currency.round(tax_data["18_taxed_base"]) * rate))
            if tax_data["16_taxed_base"] and l10n_do_ncf_type != '46':
                totals.set_MontoGravadoI2(abs(currency.round(tax_data["16_taxed_base"]) * rate))
            if tax_data["0_taxed_base"]:
                totals.set_MontoGravadoI3(abs(currency.round(tax_data["0_taxed_base"]) * rate))
            if tax_data["exempt_amount"] and l10n_do_ncf_type != '46':
                totals.set_MontoExento(abs(currency.round(tax_data["exempt_amount"]) * rate))
            if tax_data["18_taxed_base"] and l10n_do_ncf_type != '46':
                totals.set_ITBIS1(18)
            if tax_data["16_taxed_base"] and l10n_do_ncf_type != '46':
                totals.set_ITBIS2(16)
            if tax_data["0_taxed_base"]:
                totals.set_ITBIS3(0)
                totals.set_TotalITBIS(0)
            if total_taxed:
                totals.set_TotalITBIS(abs(currency.round(net_total_itbis) * rate))
            if tax_data["18_taxed_base"] and l10n_do_ncf_type != '46':
                totals.set_TotalITBIS1(abs(currency.round(net_itbis_18) * rate))
            if tax_data["16_taxed_base"] and l10n_do_ncf_type != '46':
                totals.set_TotalITBIS2(abs(currency.round(net_itbis_16) * rate))
            if tax_data["0_taxed_base"]:
                totals.set_TotalITBIS3(abs(currency.round(tax_data["0_taxed_amount"]) * rate))
        else:
            if tax_data["exempt_amount"]:
                totals.set_MontoExento(abs(currency.round(tax_data["exempt_amount"]) * rate))

        if l10n_do_ncf_type not in ("43", "44", "45", "46", "47"):
            if tax_data["itbis_withholding_amount"]:
                totals.set_TotalITBISRetenido(itbis_withholding_amount)
        if l10n_do_ncf_type not in ("43", "44", "45", "46"):
            if tax_data["isr_withholding_amount"]:
                totals.set_TotalISRRetencion(abs(
                    currency.round(tax_data["isr_withholding_amount"])
                ) * rate)

        if l10n_do_ncf_type not in ("43", "44", "47"):
            if l10n_do_ncf_type == "46":
                totals.set_MontoTotal(totals.get_MontoGravadoTotal() + totals.get_TotalITBIS())
            else:
                totals.set_MontoTotal(totals.get_MontoGravadoTotal() + totals.get_TotalITBIS() + totals.get_MontoExento())
        else:
            totals.set_MontoTotal(totals.get_MontoExento())

        return totals

    def _get_taxed_tips_data(self, details_items):
        """
            Calcula los impuestos adicionales (tips) agrupados por tipo de impuesto.

            :param details_items: Objeto con items de detalle que contienen impuestos adicionales.
            :return: Diccionario con la información agrupada por TipoImpuesto.
            """
        currency = self.currency_id
        rate = 1
        is_company_currency = self.is_company_currency()
        if not is_company_currency:
            rate = abs(
                round(1 / (self.invoice_id.amount_total / (self.invoice_id.amount_total_signed or 1) or 1), 4)
            )
        group_data = {"001": {"TipoImpuesto": "001",
                              "TasaImpuestoAdicional": 10.00,
                              "OtrosImpuestosAdicionales": 0.00,
                              },
                      "005": {"TipoImpuesto": "005",
                              "TasaImpuestoAdicional": 17.00,
                              "OtrosImpuestosAdicionales": 0.00,
                              }
                      }

        tax_cache = self.env['account.tax'].search(
            [('company_id', 'parent_of', self.company_id.ids),
             ('country_id', '=', self.env.ref("base.do").id)])

        for it in details_items.get_Item():
            if not it.get_TablaImpuestoAdicional():
                continue

            imp_ad = it.get_TablaImpuestoAdicional()
            for extra_tax in imp_ad.get_ImpuestoAdicional():
                tax_tips_id = tax_cache.filtered(lambda t: t.ecf_code == extra_tax.get_TipoImpuesto())
                if not tax_tips_id:
                    continue
                value_tax = (it.get_MontoItem() * tax_tips_id.amount) / 100
                row = group_data[extra_tax.get_TipoImpuesto()]
                row['OtrosImpuestosAdicionales'] += currency.round(value_tax) * rate

        return group_data

    def _gen_other_currency(self, cedoc, encabezado, classdoc):
        """Only used if invoice currency is not company currency

            :param object encabezado: Instancia del Encabezado del Elemento raiz.
            :param object classdoc: Clase del tipo de documento.
            """

        l10n_do_ncf_type = self.ncf_type
        currency = self.currency_id
        other_currency = classdoc.OtraMoneda()
        totals = encabezado.get_Totales()
        other_currency.set_TipoMoneda(self.currency_id.name)
        other_currency.set_TipoCambio(abs(
            1 / (self.invoice_id.amount_total / (self.invoice_id.amount_total_signed or 1) or 1)
        ))
        rate = other_currency.get_TipoCambio()
        if l10n_do_ncf_type not in ("43", "44", "47"):
            if totals.get_MontoGravadoTotal():
                other_currency.set_MontoGravadoTotalOtraMoneda(currency.round(
                    totals.get_MontoGravadoTotal()
                    / rate
                ))
            if l10n_do_ncf_type not in ("46", ) and totals.get_MontoGravadoI1():
                other_currency.set_MontoGravado1OtraMoneda(currency.round(
                    totals.get_MontoGravadoI1()
                    / rate
                ))
            if l10n_do_ncf_type not in ("46", ) and totals.get_MontoGravadoI2():
                other_currency.set_MontoGravado2OtraMoneda(currency.round(
                    totals.get_MontoGravadoI2()
                    / rate
                ))
            if totals.get_MontoGravadoI3():
                other_currency.set_MontoGravado3OtraMoneda(currency.round(
                    totals.get_MontoGravadoI3()
                    / rate
                ))

        if l10n_do_ncf_type not in ("46",) and totals.get_MontoExento():
            other_currency.set_MontoExentoOtraMoneda(currency.round(
                totals.get_MontoExento()
                / rate
            ))
        if l10n_do_ncf_type not in ("43", "44", "47") and totals.get_MontoGravadoTotal():
            other_currency.set_TotalITBISOtraMoneda(currency.round(
                totals.get_TotalITBIS()
                / rate
            ))
        if l10n_do_ncf_type not in ("43", "44", "46", '47') and totals.get_MontoGravadoI1():
            other_currency.set_TotalITBIS1OtraMoneda(currency.round(
                totals.get_TotalITBIS1()
                / rate
            ))
        if l10n_do_ncf_type not in ("43", "44", "46", "47") and totals.get_MontoGravadoI2():
            other_currency.set_TotalITBIS2OtraMoneda(currency.round(
                totals.get_TotalITBIS2()
                / rate
            ))
        if l10n_do_ncf_type not in ("43", "44", "47") and totals.get_MontoGravadoI3():
            other_currency.set_TotalITBIS3OtraMoneda(currency.round(
                totals.get_TotalITBIS3()
                / rate
            ))

        amount_total_other_currency = 0.00
        if l10n_do_ncf_type not in ("43", "44", "47"):
            amount_total_other_currency += other_currency.get_TotalITBISOtraMoneda()
        if l10n_do_ncf_type not in ("43", "44", "47"):
            amount_total_other_currency += other_currency.get_MontoGravadoTotalOtraMoneda()
        if l10n_do_ncf_type not in ("46", ):
            amount_total_other_currency += other_currency.get_MontoExentoOtraMoneda()
        if l10n_do_ncf_type not in ("43", "44", "46", "47"):
            amount_total_other_currency += other_currency.get_TotalITBIS3OtraMoneda()

        other_currency.set_MontoTotalOtraMoneda(amount_total_other_currency)
        if totals.get_MontoImpuestoAdicional():
            other_currency.set_MontoImpuestoAdicionalOtraMoneda(currency.round(
                totals.get_MontoImpuestoAdicional()
                / rate
            ))
            group_data = self._get_taxed_tips_data(cedoc.get_DetallesItems())
            imp_ads_other_currency = classdoc.ImpuestosAdicionalesOtraMoneda()
            ia_other_currency = classdoc.ImpuestoAdicionalOtraMoneda(
                                            TipoImpuestoOtraMoneda=group_data["001"]['TipoImpuesto'],
                                            TasaImpuestoAdicionalOtraMoneda=group_data["001"]['TasaImpuestoAdicional'],
                                            OtrosImpuestosAdicionalesOtraMoneda=group_data["001"][
                                                'OtrosImpuestosAdicionales'] / rate,
                                            )
            imp_ads_other_currency.add_ImpuestoAdicionalOtraMoneda(ia_other_currency)
            other_currency.set_ImpuestosAdicionalesOtraMoneda(imp_ads_other_currency)
        return other_currency

    def _get_item_withholding_vals(self, invoice_line):
        """ Returns invoice line withholding taxes values """

        line_withholding_vals = invoice_line.tax_ids.compute_all(
            price_unit=invoice_line.price_unit,
            currency=invoice_line.currency_id,
            quantity=invoice_line.quantity,
            product=invoice_line.product_id,
            partner=invoice_line.move_id.partner_id,
            is_refund=True if invoice_line.move_id.move_type == "in_refund" else False,
        )

        withholding_vals = OrderedDict()
        itbis_withhold_amount = 0.00
        isr_withhold_amount = 0.00
        for tax in line_withholding_vals["taxes"]:
            if tax["amount"] < 0:
                if self.env["account.tax"].browse(tax["id"]).tax_group_id.l10n_do_billing_indicator == 'taxable_itbis':
                    itbis_withhold_amount += tax["amount"]
                elif self.env["account.tax"].browse(tax["id"]).tax_group_id.l10n_do_billing_indicator == 'taxable_isr':
                    isr_withhold_amount += tax["amount"]

        if itbis_withhold_amount or self.ncf_type == "41":
            withholding_vals["MontoITBISRetenido"] = abs(itbis_withhold_amount)
        withholding_vals["MontoISRRetenido"] = abs(isr_withhold_amount)
        return withholding_vals

    def _gen_invoice(self, cedoc, classdoc):
        """Product lines related values

            :param object cedoc: Instancia u objeto del Elemento raiz.
            :param object classdoc: Clase del tipo de documento.

            :returns: tuple (response, vals)
            """

        details = classdoc.DetallesItems()
        is_company_currency = self.is_company_currency()
        rate = 1
        if not is_company_currency:
            rate = abs(
                round(1 / (self.invoice_id.amount_total / (self.invoice_id.amount_total_signed or 1) or 1), 4)
            )
        currency = self.currency_id
        l10n_do_ncf_type = self.ncf_type

        def get_invoicing_indicator(inv_line):
            """
            0: No Facturable
            1: ITBIS 1(18 %)
            2: ITBIS 2(16 %)
            3: ITBIS 3(0 %)
            4: Exento(E)
            """
            if l10n_do_ncf_type in ('43', '44', '47'):
                return 4

            if not inv_line.tax_ids:
                return 4
            tax_set = set(
                tax.amount
                for tax in inv_line.tax_ids
                if tax.tax_group_id.l10n_do_billing_indicator == 'taxable_itbis'
            )
            if len(tax_set) > 1 or 18 in tax_set or 1.8 in tax_set:
                return 1
            elif 16 in tax_set:
                return 2
            elif l10n_do_ncf_type == "46" and 0 in tax_set:
                return 3
            else:
                return 4

        # Lineas en positivo.
        lines = []
        if self.invoice_id:
            lines = self.invoice_id._l10n_do_ecf_invoice_line_ids()

        for i, line in enumerate(
                lines.filtered(lambda l: (l.quantity and l.price_unit >= 0)).sorted(
                    "sequence"
                ),
                1,
        ):
            total_discount = 0.00
            product_id = line.product_id
            product_name = product_id.name if product_id else (line.name or "S/N")
            item = classdoc.Item(
                NumeroLinea=i,
                NombreItem=self.limit(product_name or 'S/N', 80),
                IndicadorBienoServicio=2 if (product_id and product_id.type == "service") or l10n_do_ncf_type == "47"
                else 1,
                CantidadItem=abs(line.quantity),
                PrecioUnitarioItem=abs(
                    round(
                        line.price_unit if is_company_currency else line.price_unit * rate,
                        4,
                    )
                ),
                MontoItem=abs((line.quantity * line.price_unit) * rate),
                IndicadorFacturacion=get_invoicing_indicator(line),
            )

            if product_id and product_id.default_code:
                table_code_item = classdoc.TablaCodigosItem()
                code_item = classdoc.CodigosItem(TipoCodigo="INTERNA",
                                                 CodigoItem=self.limit(product_id.default_code, 35))
                table_code_item.add_CodigosItem(code_item)
                item.set_TablaCodigosItem(table_code_item)
            if l10n_do_ncf_type in ("34", "41", "47"):  # Tag Retencion es obligatorio en E41 y E47.
                withholding_vals = OrderedDict([("IndicadorAgenteRetencionoPercepcion", 1)])
                for k, v in self._get_item_withholding_vals(line).items():
                    withholding_vals[k] = currency.round(
                        v if is_company_currency else v * rate
                    )
                retention = classdoc.Retencion(IndicadorAgenteRetencionoPercepcion=1)
                for val in withholding_vals:
                    if val == 'MontoITBISRetenido' and withholding_vals[val]:
                        retention.set_MontoITBISRetenido(withholding_vals[val])
                    if val == 'MontoISRRetenido' and withholding_vals[val]:
                        retention.set_MontoISRRetenido(withholding_vals[val])

                if retention.get_MontoITBISRetenido() or retention.get_MontoISRRetenido():
                    item.set_Retencion(retention)

            if line.discount and l10n_do_ncf_type not in ("43", "47"):
                price_wo_discount = line.quantity * line.price_unit
                price_with_discount = price_wo_discount * (1 - (line.discount / 100.0))
                discount_amount = (
                    abs(currency.round(price_with_discount - price_wo_discount))
                    if line.discount
                    else 0
                )
                discount_amount = (
                    discount_amount
                    if is_company_currency
                    else currency.round(discount_amount * rate)
                )
                total_discount += discount_amount
                item.set_DescuentoMonto(discount_amount)
                tabla_sub_discount = classdoc.TablaSubDescuento()
                sub_discount = classdoc.SubDescuento(TipoSubDescuento="%",
                                                     SubDescuentoPorcentaje=line.discount,
                                                     MontoSubDescuento=discount_amount)
                tabla_sub_discount.add_SubDescuento(sub_discount)
                item.set_TablaSubDescuento(tabla_sub_discount)

            if total_discount:
                item.set_MontoItem(abs(item.get_MontoItem() - total_discount))
            if line.name:
                item.set_DescripcionItem(self.limit(line.name, 100))
            if line.product_uom_id:
                if not line.product_uom_id.ecf_code:
                    raise ValidationError('La unidad de medida no tiene codigo para la DGII.')
                item.set_UnidadMedida(line.product_uom_id.ecf_code)
            else:
                item.set_UnidadMedida('43')

            # Tax Tip and Other
            taxes = line.tax_ids.filtered(lambda imp: imp.tax_group_id.l10n_do_billing_indicator in ['tips', 'other'])
            if taxes:
                tabla_imp_ad = classdoc.ImpuestosAdicionales()
                for t in taxes:
                    imp1 = classdoc.ImpuestoAdicional(TipoImpuesto=t.ecf_code)
                    tabla_imp_ad.add_ImpuestoAdicional(imp1)

                item.set_TablaImpuestoAdicional(tabla_imp_ad)

            details.add_Item(item)

        # Lineas en negativo (descuentos).
        if l10n_do_ncf_type not in ('43', '47'):
            discount_charge = classdoc.DescuentosORecargos()
            for i, line in enumerate(
                    lines.filtered(
                        lambda l: l.quantity and l.price_unit < 0).sorted(
                        "sequence"
                    ),
                    1,
            ):
                discount_item = classdoc.DescuentoORecargo(NumeroLinea=i,
                                                           TipoAjuste="D",
                                                           DescripcionDescuentooRecargo=self.limit(line.name or 'S/N', 45),
                                                           TipoValor="$",
                                                           MontoDescuentooRecargo=abs(line.quantity * line.price_unit),
                                                           IndicadorFacturacionDescuentooRecargo=get_invoicing_indicator(line))
                discount_charge.add_DescuentoItem(discount_item)

            if discount_charge.get_DescuentoItem():
                cedoc.set_DescuentosORecargos(discount_charge)

        cedoc.set_DetallesItems(details)
        return cedoc

    def _gen_reference_information(self, cedoc, classdoc):
        """Informacion Referencia

            :param object cedoc: Instancia del Elemento raiz.
            :param object classdoc: Clase del tipo de documento.
            """

        info_reference = classdoc.InformacionReferencia(NCFModificado=self.invoice_id.l10n_do_origin_ncf,
                                                        FechaNCFModificado=self.invoice_id.l10n_do_ecf_date_modification,
                                                        CodigoModificacion=int(
                                                             self.invoice_id.l10n_do_ecf_modification_code or "1"),
                                                        )
        if self.invoice_id.ref:
            info_reference.set_RazonModificacion(self.invoice_id.ref)

        if self.invoice_id.l10n_do_ecf_modification_code == "2":  # TODO: Estudiar bien los CodigoModificacion (2,3,4,5).
            "Para el codigo de modificacion: 2 el comprobante debe tener un monto total igual cero."

            totals = cedoc.get_Encabezado().get_Totales()
            totals.set_MontoTotal(0.00)

        cedoc.set_InformacionReferencia(info_reference)

    def gen_heading(self):
        """Logica y validaciones del encabezado de tipo de documento.

            :returns: obj del encabezado del tipo de documento electronico.
            """

        l10n_do_ncf_type = self.ncf_type
        version = DGII_VERSION
        invoice_id = self.invoice_id
        indicator_amount_taxable = int(
            any(
                True
                for t in invoice_id.invoice_line_ids.tax_ids.filtered(
                    lambda tax: tax.tax_group_id.l10n_do_billing_indicator == 'taxable_itbis' and tax.amount == 18
                )
                if t.price_include
            )
        )

        if l10n_do_ncf_type == "31":
            """Factura de Credito Fiscal Electronica"""
            if not self.name:
                raise ValidationError('No esta definida la secuencia para este tipo de documento.')
            if not invoice_id.l10n_do_ncf_expiration_date:
                raise ValidationError(
                    'No esta definida la fecha de vencimiento de la secuencia para este tipo de comprobante.')

            classdoc = E31
            IdDoc = classdoc.IdDoc(TipoeCF=l10n_do_ncf_type,
                                   eNCF=self.name,
                                   FechaVencimientoSecuencia=invoice_id.l10n_do_ncf_expiration_date,
                                   TipoIngresos=invoice_id.l10n_do_income_type,
                                   TipoPago=self.get_payment_type(),
                                   )
            IdDoc.set_IndicadorMontoGravado(indicator_amount_taxable)
            if IdDoc.get_TipoPago() == 2:  # Pago a credito
                IdDoc.set_FechaLimitePago(invoice_id.invoice_date_due)
            if invoice_id.invoice_payment_term_id:
                delta = invoice_id.invoice_date_due - invoice_id.invoice_date
                IdDoc.set_TerminoPago(self.limit("%s días" % delta.days, 15))

            sender = self.gen_sender(classdoc)
            buyer = self.gen_buyer(classdoc)
            heading = classdoc.Encabezado(Version=version,
                                          IdDoc=IdDoc,
                                          Emisor=sender,
                                          Comprador=buyer,
                                          Totales=None,
                                          )

            return heading
        elif l10n_do_ncf_type == '32':
            """Factura de Consumo Electronica"""
            if not self.name:
                raise ValidationError('No esta definida la secuencia para este tipo de documento.')

            classdoc = E32
            IdDoc = classdoc.IdDoc(TipoeCF=l10n_do_ncf_type,
                                   eNCF=self.name,
                                   TipoIngresos=invoice_id.l10n_do_income_type,
                                   TipoPago=self.get_payment_type(),
                                   )
            IdDoc.set_IndicadorMontoGravado(indicator_amount_taxable)
            if IdDoc.get_TipoPago() == 2:  # Pago a credito
                IdDoc.set_FechaLimitePago(invoice_id.invoice_date_due)
            if invoice_id.invoice_payment_term_id:
                delta = invoice_id.invoice_date_due - invoice_id.invoice_date
                IdDoc.set_TerminoPago(self.limit("%s días" % int(delta.days), 15))

            sender = self.gen_sender(classdoc)
            buyer = self.gen_buyer(classdoc)
            heading = classdoc.Encabezado(Version=version,
                                          IdDoc=IdDoc,
                                          Emisor=sender,
                                          Comprador=buyer,
                                          Totales=None,
                                          )

            return heading
        elif l10n_do_ncf_type == '33':
            """Nota de Débito Electrónica"""
            if not self.name:
                raise ValidationError('No esta definida la secuencia para este tipo de documento.')
            if not invoice_id.l10n_do_ncf_expiration_date:
                raise ValidationError(
                    'No esta definida la fecha de vencimiento de la secuencia para este tipo de comprobante.')

            classdoc = E33
            IdDoc = classdoc.IdDoc(TipoeCF=l10n_do_ncf_type,
                                   eNCF=self.name,
                                   FechaVencimientoSecuencia=invoice_id.l10n_do_ncf_expiration_date,
                                   TipoIngresos=invoice_id.l10n_do_income_type,
                                   TipoPago=self.get_payment_type(),
                                   )

            IdDoc.set_IndicadorMontoGravado(indicator_amount_taxable)
            if IdDoc.get_TipoPago() == 2:  # Pago a credito
                IdDoc.set_FechaLimitePago(invoice_id.invoice_date_due)
            if invoice_id.invoice_payment_term_id:
                delta = invoice_id.invoice_date_due - invoice_id.invoice_date
                IdDoc.set_TerminoPago(self.limit("%s días" % int(delta.days), 15))

            sender = self.gen_sender(classdoc)
            buyer = self.gen_buyer(classdoc)
            heading = classdoc.Encabezado(Version=version,
                                          IdDoc=IdDoc,
                                          Emisor=sender,
                                          Comprador=buyer,
                                          Totales=None,
                                          )

            return heading
        elif l10n_do_ncf_type == '34':
            """Nota de Crédito Electrónica"""
            if not self.name:
                raise ValidationError('No esta definida la secuencia para este tipo de documento.')

            classdoc = E34
            delta = invoice_id.invoice_date - (invoice_id.l10n_do_ecf_date_modification or invoice_id.invoice_date)
            IdDoc = classdoc.IdDoc(TipoeCF=l10n_do_ncf_type,
                                   eNCF=self.name,
                                   TipoIngresos=invoice_id.l10n_do_income_type,
                                   TipoPago=self.get_payment_type(),
                                   IndicadorNotaCredito=int(delta.days > 30),
                                   )

            IdDoc.set_IndicadorMontoGravado(indicator_amount_taxable)
            if self.company_id.l10n_do_ecf_deferred_submissions:
                IdDoc.set_IndicadorEnvioDiferido(1)
            if invoice_id.invoice_date_due:
                IdDoc.set_FechaLimitePago(invoice_id.invoice_date_due)

            sender = self.gen_sender(classdoc)
            buyer = self.gen_buyer(classdoc)
            heading = classdoc.Encabezado(Version=version,
                                          IdDoc=IdDoc,
                                          Emisor=sender,
                                          Comprador=buyer,
                                          Totales=None,
                                          )

            return heading
        elif l10n_do_ncf_type == '41':
            """Compras Electrónico"""
            if not self.name:
                raise ValidationError('No esta definida la secuencia para este tipo de documento.')

            if (not invoice_id.l10n_do_ncf_expiration_date and invoice_id.l10n_do_fiscal_sequence_id
                    and invoice_id.l10n_do_fiscal_sequence_id.expiration_date):
                l10n_do_ncf_expiration_date = invoice_id.l10n_do_fiscal_sequence_id.expiration_date
            else:
                l10n_do_ncf_expiration_date = invoice_id.l10n_do_ncf_expiration_date

            if not l10n_do_ncf_expiration_date:
                raise ValidationError(
                    'No esta definida la fecha de vencimiento de la secuencia para este tipo de comprobante.')
            if not l10n_do_ncf_expiration_date:
                raise ValidationError(
                    'No esta definida la fecha de vencimiento de la secuencia para este tipo de comprobante.')

            classdoc = E41
            IdDoc = classdoc.IdDoc(TipoeCF=l10n_do_ncf_type,
                                   eNCF=self.name,
                                   FechaVencimientoSecuencia=l10n_do_ncf_expiration_date,
                                   TipoPago=self.get_payment_type(),
                                   )

            IdDoc.set_IndicadorMontoGravado(indicator_amount_taxable)
            if IdDoc.get_TipoPago() == 2:  # Pago a credito
                IdDoc.set_FechaLimitePago(invoice_id.invoice_date_due)
            if invoice_id.invoice_payment_term_id:
                delta = invoice_id.invoice_date_due - invoice_id.invoice_date
                IdDoc.set_TerminoPago(self.limit("%s días" % delta.days, 15))

            sender = self.gen_sender(classdoc)
            buyer = self.gen_buyer(classdoc)
            heading = classdoc.Encabezado(Version=version,
                                          IdDoc=IdDoc,
                                          Emisor=sender,
                                          Comprador=buyer,
                                          Totales=None,
                                          )

            return heading
        elif l10n_do_ncf_type == '43':
            """Gastos Menores Electrónico"""
            if not self.name:
                raise ValidationError('No esta definida la secuencia para este tipo de documento.')

            if (not invoice_id.l10n_do_ncf_expiration_date and invoice_id.l10n_do_fiscal_sequence_id
                    and invoice_id.l10n_do_fiscal_sequence_id.expiration_date):
                l10n_do_ncf_expiration_date = invoice_id.l10n_do_fiscal_sequence_id.expiration_date
            else:
                l10n_do_ncf_expiration_date = invoice_id.l10n_do_ncf_expiration_date

            if not l10n_do_ncf_expiration_date:
                raise ValidationError(
                    'No esta definida la fecha de vencimiento de la secuencia para este tipo de comprobante.')

            classdoc = E43
            IdDoc = classdoc.IdDoc(TipoeCF=l10n_do_ncf_type,
                                   eNCF=self.name,
                                   FechaVencimientoSecuencia=l10n_do_ncf_expiration_date,
                                   )

            sender = self.gen_sender(classdoc)
            heading = classdoc.Encabezado(Version=version,
                                          IdDoc=IdDoc,
                                          Emisor=sender,
                                          Totales=None,
                                          )

            return heading
        elif l10n_do_ncf_type == '44':
            """Regímenes Especiales Electrónico"""
            if not self.name:
                raise ValidationError('No esta definida la secuencia para este tipo de documento.')

            if (not invoice_id.l10n_do_ncf_expiration_date and invoice_id.l10n_do_fiscal_sequence_id
                    and invoice_id.l10n_do_fiscal_sequence_id.expiration_date):
                l10n_do_ncf_expiration_date = invoice_id.l10n_do_fiscal_sequence_id.expiration_date
            else:
                l10n_do_ncf_expiration_date = invoice_id.l10n_do_ncf_expiration_date

            if not l10n_do_ncf_expiration_date:
                raise ValidationError(
                    'No esta definida la fecha de vencimiento de la secuencia para este tipo de comprobante.')

            classdoc = E44
            IdDoc = classdoc.IdDoc(TipoeCF=l10n_do_ncf_type,
                                   eNCF=self.name,
                                   FechaVencimientoSecuencia=l10n_do_ncf_expiration_date,
                                   TipoIngresos=invoice_id.l10n_do_income_type,
                                   TipoPago=self.get_payment_type(),
                                   )

            if IdDoc.get_TipoPago() == 2:  # Pago a credito
                IdDoc.set_FechaLimitePago(invoice_id.invoice_date_due)
            if invoice_id.invoice_payment_term_id:
                delta = invoice_id.invoice_date_due - invoice_id.invoice_date
                IdDoc.set_TerminoPago(self.limit("%s días" % delta.days, 15))

            sender = self.gen_sender(classdoc)
            buyer = self.gen_buyer(classdoc)
            heading = classdoc.Encabezado(Version=version,
                                          IdDoc=IdDoc,
                                          Emisor=sender,
                                          Comprador=buyer,
                                          Totales=None,
                                          )

            return heading
        elif l10n_do_ncf_type == '45':
            """Gubernamental Electrónico"""
            if not self.name:
                raise ValidationError('No esta definida la secuencia para este tipo de documento.')

            if (not invoice_id.l10n_do_ncf_expiration_date and invoice_id.l10n_do_fiscal_sequence_id
                    and invoice_id.l10n_do_fiscal_sequence_id.expiration_date):
                l10n_do_ncf_expiration_date = invoice_id.l10n_do_fiscal_sequence_id.expiration_date
            else:
                l10n_do_ncf_expiration_date = invoice_id.l10n_do_ncf_expiration_date

            if not l10n_do_ncf_expiration_date:
                raise ValidationError(
                    'No esta definida la fecha de vencimiento de la secuencia para este tipo de comprobante.')

            classdoc = E45
            IdDoc = classdoc.IdDoc(TipoeCF=l10n_do_ncf_type,
                                   eNCF=self.name,
                                   FechaVencimientoSecuencia=l10n_do_ncf_expiration_date,
                                   TipoIngresos=invoice_id.l10n_do_income_type,
                                   TipoPago=self.get_payment_type(),
                                   )

            IdDoc.set_IndicadorMontoGravado(indicator_amount_taxable)
            if IdDoc.get_TipoPago() == 2:  # Pago a credito
                IdDoc.set_FechaLimitePago(invoice_id.invoice_date_due)
            if invoice_id.invoice_payment_term_id:
                delta = invoice_id.invoice_date_due - invoice_id.invoice_date
                IdDoc.set_TerminoPago(self.limit("%s días" % delta.days, 15))

            sender = self.gen_sender(classdoc)
            buyer = self.gen_buyer(classdoc)
            heading = classdoc.Encabezado(Version=version,
                                          IdDoc=IdDoc,
                                          Emisor=sender,
                                          Comprador=buyer,
                                          Totales=None,
                                          )

            return heading
        elif l10n_do_ncf_type == '46':
            """Comprobante de Exportaciones Electrónico"""
            if not self.name:
                raise ValidationError('No esta definida la secuencia para este tipo de documento.')

            if (not invoice_id.l10n_do_ncf_expiration_date and invoice_id.l10n_do_fiscal_sequence_id
                    and invoice_id.l10n_do_fiscal_sequence_id.expiration_date):
                l10n_do_ncf_expiration_date = invoice_id.l10n_do_fiscal_sequence_id.expiration_date
            else:
                l10n_do_ncf_expiration_date = invoice_id.l10n_do_ncf_expiration_date

            if not l10n_do_ncf_expiration_date:
                raise ValidationError(
                    'No esta definida la fecha de vencimiento de la secuencia para este tipo de comprobante.')

            classdoc = E46
            IdDoc = classdoc.IdDoc(TipoeCF=l10n_do_ncf_type,
                                   eNCF=self.name,
                                   FechaVencimientoSecuencia=l10n_do_ncf_expiration_date,
                                   TipoIngresos=invoice_id.l10n_do_income_type,
                                   TipoPago=self.get_payment_type(),
                                   )

            if IdDoc.get_TipoPago() == 2:  # Pago a credito
                IdDoc.set_FechaLimitePago(invoice_id.invoice_date_due)
            if invoice_id.invoice_payment_term_id:
                delta = invoice_id.invoice_date_due - invoice_id.invoice_date
                IdDoc.set_TerminoPago(self.limit("%s días" % delta.days, 15))

            sender = self.gen_sender(classdoc)
            buyer = self.gen_buyer(classdoc)
            heading = classdoc.Encabezado(Version=version,
                                          IdDoc=IdDoc,
                                          Emisor=sender,
                                          Comprador=buyer,
                                          Totales=None,
                                          )

            return heading
        elif l10n_do_ncf_type == '47':
            """Comprobante para Pagos al Exterior Electrónico"""
            if not self.name:
                raise ValidationError('No esta definida la secuencia para este tipo de documento.')

            if (not invoice_id.l10n_do_ncf_expiration_date and invoice_id.l10n_do_fiscal_sequence_id
                    and invoice_id.l10n_do_fiscal_sequence_id.expiration_date):
                l10n_do_ncf_expiration_date = invoice_id.l10n_do_fiscal_sequence_id.expiration_date
            else:
                l10n_do_ncf_expiration_date = invoice_id.l10n_do_ncf_expiration_date

            if not l10n_do_ncf_expiration_date:
                raise ValidationError(
                    'No esta definida la fecha de vencimiento de la secuencia para este tipo de comprobante.')

            classdoc = E47
            IdDoc = classdoc.IdDoc(TipoeCF=l10n_do_ncf_type,
                                   eNCF=self.name,
                                   FechaVencimientoSecuencia=l10n_do_ncf_expiration_date,
                                   )

            if IdDoc.get_TipoPago() == 2:  # Pago a credito
                IdDoc.set_FechaLimitePago(invoice_id.invoice_date_due)
            if invoice_id.invoice_payment_term_id:
                delta = invoice_id.invoice_date_due - invoice_id.invoice_date
                IdDoc.set_TerminoPago(self.limit("%s días" % delta.days, 15))

            sender = self.gen_sender(classdoc)
            buyer = self.gen_buyer(classdoc)
            heading = classdoc.Encabezado(Version=version,
                                          IdDoc=IdDoc,
                                          Emisor=sender,
                                          Comprador=buyer,
                                          Totales=None,
                                          )
            return heading

    def gen_buyer(self, classdoc):
        """Logica y validaciones del comprador de tipo de documento.

            :param object classdoc: Clase del tipo de documento.
            :returns: obj del comprador del tipo de documento electronico.
            """

        if not self.partner_id:
            return None

        def validate_and_dpa():
            if self.partner_id.country_id == self.env.ref("base.do"):
                if self.partner_id.state_id and not self.partner_id.state_id.ecf_code:
                    raise ValidationError('La Provincia seleccionada no tiene codigo para DGII.')
                if self.partner_id.res_municipality_id and not self.partner_id.res_municipality_id.ecf_code:
                    raise ValidationError('El municipio seleccionada no tiene codigo para DGII.')

        partner_id = self.partner_id
        l10n_do_ncf_type = self.ncf_type
        if l10n_do_ncf_type in ["31", "41", "44", "45", "46", "47"]:
            required_fields = self.env["ecf.document"]._l10n_do_validate_partner(partner_id)
            if required_fields:
                raise ValidationError(
                    _("The selected partner has missing required fields:\n%s", "\n".join(required_fields))
                )

        if l10n_do_ncf_type == "31":
            """Credito Fiscal Electronica"""

            validate_and_dpa()
            buyer = classdoc.Comprador(RNCComprador=partner_id.vat,
                                       RazonSocialComprador=self.limit(partner_id.name, 150),
                                       )
            if partner_id.phone:
                phone = partner_id.phone.strip()
                if re.match(r"^.{1,80}$", phone):
                    buyer.set_ContactoComprador(self.limit(phone, 80))
            if partner_id.email:
                email = partner_id.email.lower()
                email = email.strip()
                if re.match("[^@]+@[^@]+\\.[^@]+", email):
                    buyer.set_CorreoComprador(self.limit(email, 80))
            if partner_id.street:
                buyer.set_DireccionComprador(self.limit(partner_id.street, 100))
            if partner_id.res_municipality_id:
                buyer.set_MunicipioComprador(partner_id.res_municipality_id.ecf_code)
            if partner_id.state_id:
                buyer.set_ProvinciaComprador(partner_id.state_id.ecf_code)

            return buyer
        elif l10n_do_ncf_type == '32':
            """Consumo Electronica"""
            partner_vat = partner_id.vat or ""
            amount_total_signed = self.xml_amount_untaxed_signed
            if amount_total_signed >= 250000:
                required_fields = self.env["ecf.document"]._l10n_do_validate_partner(partner_id)
                if required_fields:
                    raise ValidationError(
                        _("For amount >= 25000 has missing required fields:\n%s", "\n".join(required_fields))
                    )

            validate_and_dpa()
            buyer = classdoc.Comprador(RazonSocialComprador=self.limit(partner_id.name, 80))
            if self.is_l10n_do_partner() and partner_vat:
                buyer.set_RNCComprador(partner_vat)
            elif not self.is_l10n_do_partner() and partner_vat and self.xml_amount_untaxed_signed >= 250000:
                buyer.set_IdentificadorExtranjero(partner_vat)

            if partner_id.phone:
                phone = partner_id.phone.strip()
                if re.match(r"^.{1,80}$", phone):
                    buyer.set_ContactoComprador(self.limit(phone, 80))
            if partner_id.email:
                email = partner_id.email.lower()
                email = email.strip()
                if re.match("[^@]+@[^@]+\\.[^@]+", email):
                    buyer.set_CorreoComprador(self.limit(email, 80))
            if partner_id.street:
                buyer.set_DireccionComprador(self.limit(partner_id.street, 100))
            if self.is_l10n_do_partner() and partner_id.res_municipality_id:
                buyer.set_MunicipioComprador(partner_id.res_municipality_id.ecf_code)
            if self.is_l10n_do_partner() and partner_id.state_id:
                buyer.set_ProvinciaComprador(partner_id.state_id.ecf_code)

            return buyer
        elif l10n_do_ncf_type == '33':
            """Nota de Débito Electrónica"""
            partner_vat = self.partner_id.vat or ""
            amount_total_signed = self.invoice_id.amount_total_signed
            if float_compare(amount_total_signed, float(250000.00), 2) == 1:
                required_fields = self.env["ecf.document"]._l10n_do_validate_partner(partner_id)
                if required_fields:
                    raise ValidationError(
                        _("For amount >= 2500 has missing required fields:\n%s", "\n".join(required_fields))
                    )

            buyer = classdoc.Comprador(RazonSocialComprador=self.limit(partner_id.name, 80))
            if self.is_l10n_do_partner():
                buyer.set_RNCComprador(partner_vat)
            else:
                buyer.set_IdentificadorExtranjero(partner_vat)

            if partner_id.phone:
                phone = partner_id.phone.strip()
                if re.match(r"^.{1,80}$", phone):
                    buyer.set_ContactoComprador(self.limit(phone, 80))
            if partner_id.email:
                email = partner_id.email.lower()
                email = email.strip()
                if re.match("[^@]+@[^@]+\\.[^@]+", email):
                    buyer.set_CorreoComprador(self.limit(email, 80))
            if partner_id.street:
                buyer.set_DireccionComprador(self.limit(partner_id.street, 100))
            if self.is_l10n_do_partner() and partner_id.res_municipality_id:
                buyer.set_MunicipioComprador(partner_id.res_municipality_id.ecf_code)
            if self.is_l10n_do_partner() and partner_id.state_id:
                buyer.set_ProvinciaComprador(partner_id.state_id.ecf_code)

            return buyer
        elif l10n_do_ncf_type == '34':
            """Nota de Crédito Electrónica"""
            buyer = classdoc.Comprador()
            buyer.set_RazonSocialComprador(self.limit(partner_id.name, 80))

            if partner_id.vat and self.is_l10n_do_partner():
                buyer.set_RNCComprador(partner_id.vat)
            elif partner_id.vat and not self.is_l10n_do_partner():
                buyer.set_IdentificadorExtranjero(partner_id.vat)

            if partner_id.email:
                email = self.partner_id.email.lower()
                email = email.strip()
                if re.match("[^@]+@[^@]+\\.[^@]+", email):
                    buyer.set_CorreoComprador(self.limit(email, 80))
            if partner_id.street:
                buyer.set_DireccionComprador(self.limit(partner_id.street, 100))
            if self.is_l10n_do_partner() and partner_id.res_municipality_id:
                buyer.set_MunicipioComprador(partner_id.res_municipality_id.ecf_code)
            if self.is_l10n_do_partner() and partner_id.state_id:
                buyer.set_ProvinciaComprador(partner_id.state_id.ecf_code)

            return buyer
        elif l10n_do_ncf_type == '41':
            """Compras Electrónico"""

            buyer = classdoc.Comprador(RNCComprador=partner_id.vat,
                                       RazonSocialComprador=self.limit(partner_id.name, 150),
                                       )
            if partner_id.email:
                email = partner_id.email.lower()
                email = email.strip()
                if re.match("[^@]+@[^@]+\\.[^@]+", email):
                    buyer.set_CorreoComprador(self.limit(email, 80))
            if partner_id.street:
                buyer.set_DireccionComprador(self.limit(partner_id.street, 100))
            if self.is_l10n_do_partner() and partner_id.res_municipality_id:
                buyer.set_MunicipioComprador(partner_id.res_municipality_id.ecf_code)
            if self.is_l10n_do_partner() and partner_id.state_id:
                buyer.set_ProvinciaComprador(partner_id.state_id.ecf_code)

            return buyer
        elif l10n_do_ncf_type in ['44', '45']:
            """Regímenes Especiales Electrónico y Gubernamental Electrónico"""

            validate_and_dpa()
            buyer = classdoc.Comprador(RNCComprador=partner_id.vat,
                                       RazonSocialComprador=self.limit(partner_id.name, 150),
                                       )
            if partner_id.email:
                email = self.partner_id.email.lower()
                email = email.strip()
                if re.match("[^@]+@[^@]+\\.[^@]+", email):
                    buyer.set_CorreoComprador(self.limit(email, 80))
            if partner_id.street:
                buyer.set_DireccionComprador(self.limit(partner_id.street, 100))
            if self.is_l10n_do_partner() and partner_id.res_municipality_id:
                buyer.set_MunicipioComprador(partner_id.res_municipality_id.ecf_code)
            if self.is_l10n_do_partner() and partner_id.state_id:
                buyer.set_ProvinciaComprador(partner_id.state_id.ecf_code)

            return buyer
        elif l10n_do_ncf_type == '46':
            """Comprobante de Exportaciones Electrónico"""

            validate_and_dpa()
            buyer = classdoc.Comprador(RazonSocialComprador=self.limit(partner_id.name, 150))
            if self.is_l10n_do_partner() and partner_id.vat:
                buyer.set_RNCComprador(partner_id.vat)
            elif not self.is_l10n_do_partner() and partner_id.vat:
                buyer.set_IdentificadorExtranjero(partner_id.vat)

            if partner_id.email:
                email = partner_id.email.lower()
                email = email.strip()
                if re.match("[^@]+@[^@]+\\.[^@]+", email):
                    buyer.set_CorreoComprador(self.limit(email, 80))
            if partner_id.street:
                buyer.set_DireccionComprador(self.limit(partner_id.street, 100))
            if self.is_l10n_do_partner() and partner_id.res_municipality_id:
                buyer.set_MunicipioComprador(partner_id.res_municipality_id.ecf_code)
            if self.is_l10n_do_partner() and partner_id.state_id:
                buyer.set_ProvinciaComprador(partner_id.state_id.ecf_code)
            if partner_id.country_id:
                buyer.set_PaisComprador(partner_id.country_id.name)

            return buyer
        elif l10n_do_ncf_type == '47':
            """Comprobante para Pagos al Exterior Electrónico"""

            buyer = classdoc.Comprador(RazonSocialComprador=self.limit(partner_id.name, 150))
            if partner_id.vat:
                buyer.set_IdentificadorExtranjero(partner_id.vat)

            return buyer

    @api.model
    def _l10n_do_validate_partner(self, partner):
        if not partner:
            return []

        errors = []
        required_fields = ("name", "vat", )
        for field in required_fields:
            if not partner[field]:
                errors.append(
                    _(
                        "%(field)s on partner %(partner)s is required for e-invoicing",
                        field=partner._fields[field].string,
                        partner=partner.display_name,
                    )
                )

        return errors

    def _gen_cedoc(self):
        """ Retorna el elemento raiz de un documento electronico.

            :returns: obj del tipo de documento electronico.
            """
        is_company_currency = self.is_company_currency()

        def prepare_tax_tips_and_additional_xml_amounts(totales_vals):
            do_ncf_type = self.ncf_type
            rate = 1
            if not is_company_currency:
                rate = abs(
                    round(1 / (self.invoice_id.amount_total / (self.invoice_id.amount_total_signed or 1) or 1), 4)
                )

            tax_data = self.get_taxed_amount_data()
            group_data = self._get_taxed_tips_data(cedoc.get_DetallesItems())
            additional_amounts = (
                ("tax_additional", "001"),
                ("tax_additional_other", "005"),
            )

            for tax_field, group_key in additional_amounts:
                additional_amount = tax_data[tax_field]
                if additional_amount and do_ncf_type not in ("41", "43", "46", "47"):
                    totals.set_MontoTotal(totals.get_MontoTotal() + additional_amount)
                    totals.set_MontoImpuestoAdicional(additional_amount * rate)

                    imp_ads = classdoc.ImpuestosAdicionales()
                    group_value = group_data[group_key]
                    ia = classdoc.ImpuestoAdicional(
                        TipoImpuesto=group_value["TipoImpuesto"],
                        TasaImpuestoAdicional=group_value["TasaImpuestoAdicional"],
                        OtrosImpuestosAdicionales=group_value["OtrosImpuestosAdicionales"],
                    )
                    imp_ads.add_ImpuestoAdicional(ia)
                    totals.set_ImpuestosAdicionales(imp_ads)

            if do_ncf_type not in ("43", "44", "47"):
                self.xml_amount_tax = totales_vals.get_TotalITBIS()

            self.xml_amount_total = totales_vals.get_MontoTotal()

        l10n_do_ncf_type = self.ncf_type
        if l10n_do_ncf_type in ['31', '32', '41', '43', '44', '45', '46', '47']:
            encabezado = self.gen_heading()
            if l10n_do_ncf_type == '31':
                classdoc = E31
                cedoc = classdoc.FacturaCreditoFiscalElectronica(Encabezado=encabezado)
            elif l10n_do_ncf_type == '32':
                classdoc = E32
                cedoc = classdoc.FacturaConsumoElectronica(Encabezado=encabezado)
            elif l10n_do_ncf_type == '41':
                classdoc = E41
                cedoc = E41.ComprasElectronica(Encabezado=encabezado)
            elif l10n_do_ncf_type == '43':
                classdoc = E43
                cedoc = E43.GastosMenoresElectronico(Encabezado=encabezado)
            elif l10n_do_ncf_type == '44':
                classdoc = E44
                cedoc = E44.RegimenesEspecialesElectronico(Encabezado=encabezado)
            elif l10n_do_ncf_type == '45':
                classdoc = E45
                cedoc = E45.GubernamentalElectronico(Encabezado=encabezado)
            elif l10n_do_ncf_type == '46':
                classdoc = E46
                cedoc = E46.ComprobanteExportacionesElectronico(Encabezado=encabezado)
            else:
                classdoc = E47
                cedoc = E47.ComprobantePagosExteriorElectronico(Encabezado=encabezado)

            totals = self.gen_totals(classdoc)
            encabezado.set_Totales(totals)

            if l10n_do_ncf_type not in ['34', '43']:
                id_doc = encabezado.get_IdDoc()
                id_doc.set_TablaFormasPago(self.get_payment_way(classdoc))

            if self.invoice_id:
                cedoc = self._gen_invoice(cedoc, classdoc)

            prepare_tax_tips_and_additional_xml_amounts(totals)
            if not is_company_currency:
                other_currency = self._gen_other_currency(cedoc, encabezado, classdoc)
                encabezado.set_OtraMoneda(other_currency)

            return cedoc
        elif l10n_do_ncf_type == '33':
            """Nota de Débito Electrónica"""
            classdoc = E33
            encabezado = self.gen_heading()
            cedoc = classdoc.NotaDebitoElectronica(Encabezado=encabezado)
            totals = self.gen_totals(classdoc)
            encabezado.set_Totales(totals)

            if self.invoice_id:
                cedoc = self._gen_invoice(cedoc, classdoc)

            prepare_tax_tips_and_additional_xml_amounts(totals)
            if not is_company_currency:
                other_currency = self._gen_other_currency(cedoc, encabezado, classdoc)
                encabezado.set_OtraMoneda(other_currency)

            self._gen_reference_information(cedoc, classdoc)
            return cedoc
        elif l10n_do_ncf_type == '34':
            """Nota de Crédito Electrónica"""
            if not self.invoice_id.l10n_do_origin_ncf:
                raise ValidationError(_("Could not exist origin document."))

            classdoc = E34
            encabezado = self.gen_heading()
            cedoc = classdoc.NotaCreditoElectronica(Encabezado=encabezado)
            totals = self.gen_totals(classdoc)
            encabezado.set_Totales(totals)

            if self.invoice_id:
                cedoc = self._gen_invoice(cedoc, classdoc)
            prepare_tax_tips_and_additional_xml_amounts(totals)
            if not is_company_currency:
                other_currency = self._gen_other_currency(cedoc, encabezado, classdoc)
                encabezado.set_OtraMoneda(other_currency)
            self._gen_reference_information(cedoc, classdoc)
            return cedoc

    def sign_doc(self, filename, rfcf=False):
        ceconfig = self.company_id._filter_ceconfig_by_company()
        ecf_name = self.company_id.vat + "" + self.name
        signed_filename = "/tmp/{}.xml".format(ecf_name)
        os.rename(filename, signed_filename)
        xml_f = open(signed_filename, 'rb')
        xml_file = xml_f.read()
        dgii_api = DGIIApi(ceconfig)
        xml_encoded = bytes(xml_file)
        if os.path.exists(signed_filename):
            os.remove(signed_filename)

        try:
            _xml = etree.XML(xml_encoded, parser=parser)
            xml_signed = ceconfig._sign(dgii_api, _xml)
        except Exception as e:
            msg = e
            _logger.error(e)
            raise UserError(str(msg) + "\n" + 'Error al firmar: Compruebe las credenciales.')

        if rfcf:
            _logger.info("##### RFCE FIRMADO: " + signed_filename)
            return xml_signed

        _logger.info("##### ECF FIRMADO: " + signed_filename)
        document_values = {
            "xml_file": base64.b64encode(xml_signed),
            "xml_file_name": "{}.xml".format(ecf_name),
            "l10n_do_ecf_send_state": 'signed_pending',
            "date_signed": fields.Datetime.now(),
        }
        document_values.update({"QR_code": self._generate_barcode(document_values, xml_signed, ceconfig.environment)})
        self.write(document_values)
        xml_f.close()
        return True

    def _gen_xml_rfce(self):
        ceconfig = self.company_id._filter_ceconfig_by_company()
        lib = libRFCE.libRFCE(self, ceconfig)
        classdoc = RFCE
        encabezado = lib.gen_encabezado()
        rfce = classdoc.ResumenFacturaConsumoElectronica(Encabezado=encabezado)
        data = base64.b64decode(self.xml_file)
        ecf = ET.fromstring(data)
        signature_value = ecf.findall('{http://www.w3.org/2000/09/xmldsig#}Signature')[0].find(
            '{http://www.w3.org/2000/09/xmldsig#}SignatureValue').text
        code_security = signature_value[0:6]
        encabezado.set_CodigoSeguridadeCF(code_security)
        file = tempfile.NamedTemporaryFile(delete=False)
        file.write(b'<?xml version="1.0" encoding="utf-8"?>')
        rfce.export(file, 0, namespacedef_="", pretty_print=False)
        file.write(b'\n')
        file.close()
        xml_file = self.sign_doc(file.name, True)
        self.write({
            "xml_rfce_file": base64.b64encode(xml_file),
            "xml_rfce_file_name": "RFECF_%s.xml" % self.name,
        })

    def _send_to_dgii(self):
        ceconfig = self.company_id._filter_ceconfig_by_company()
        dgii_api = DGIIApi(ceconfig)

        if not self.xml_file:
            # self.action_gen_xml()
            if not self.env.context.get('cron_skip_connection_errs'):
                raise UserError("Se debe crear primero el XML antes de enviar a la DGII.")
            return

        if self.is_rfce:
            return self.receipt_rfce(dgii_api)
        else:
            return self.receipt_ecf(dgii_api)

    def receipt_ecf(self, dgii_api):
        kernel = dgii_api.get_token_semilla()
        if not isinstance(kernel, dict):
            if not self.env.context.get('cron_skip_connection_errs'):
                raise ValidationError("No se pudo obtener la semilla: %s" % kernel)
            return

        if not self.xml_file:
            return False

        response, vals = dgii_api.receipt_xml_ecf(base64.b64decode(self.xml_file), self.xml_file_name)
        if response is None:
            self.message_detail_dgii = f"DGII error: {vals.get('error')}"
            return False

        self.response_status_code = response.status_code
        if response.status_code == 200:
            response, vals = dgii_api.send_ecf_submit_request_trackId(vals.get("token"), vals.get("trackId"))
            data_dict = xmltodict.parse(vals)
            document_vals = {
                'xml_dgii_file_name': 'ECF_%s.xml' % self.name,
                'xml_dgii_file': base64.b64encode(bytes(vals.encode('utf-8'))),
                'l10n_do_ecf_send_state': ECF_STATE_MAP[data_dict.get('RespuestaConsultaTrackId').get('Estado')],
                'message_detail_dgii': self._prepare_msg_ECF_vals(data_dict),
                'state': 'invoice_sent',
                'sequence_used': True if data_dict.get('RespuestaConsultaTrackId').get(
                    'SecuenciaUtilizada') == 'true' else False,
            }
            self.write(document_vals)
        else:
            response_text = response.text
            _logger.error(response_text)
            return False

    def receipt_rfce(self, dgii_api):
        kernel = dgii_api.get_token_semilla()
        if not isinstance(kernel, dict):
            if not self.env.context.get('cron_skip_connection_errs'):
                raise ValidationError("No se pudo obtener la semilla: %s" % kernel)
            return

        if not self.xml_rfce_file:
            return False

        xml_file = base64.b64decode(self.xml_rfce_file)
        response, vals = dgii_api.receipt_xml_rfce(xml_file, self.xml_file_name)
        if response is None:
            raise ValidationError(f"DGII error: {vals.get('error')}")

        self.response_status_code = response.status_code
        if response.status_code == 200:
            data_dict = xmltodict.parse(vals)
            document_vals = {
                'xml_dgii_file_name': 'RFECF_%s.xml' % self.name,
                'xml_dgii_file': base64.b64encode(bytes(vals.encode('utf-8'))),
                'l10n_do_ecf_send_state': ECF_STATE_MAP[data_dict.get('Respuesta').get('Estado')],
                'message_detail_dgii': self._prepare_msg_RFECF_vals(data_dict),
                'state': 'invoice_sent',
                'sequence_used': True if data_dict.get('Respuesta').get(
                    'SecuenciaUtilizada') == 'true' else False,
            }

            self.write(document_vals)
        elif response.status_code == 400:
            if response.headers["Content-Type"] == 'application/xml; charset=utf-8':
                data_dict = xmltodict.parse(vals)
                document_vals = {
                    'xml_dgii_file_name': 'RFECF_%s.xml' % self.name,
                    'xml_dgii_file': base64.b64encode(bytes(vals.encode('utf-8'))),
                    'l10n_do_ecf_send_state': ECF_STATE_MAP[data_dict.get('Respuesta').get('Estado')],
                    'message_detail_dgii': self._prepare_msg_RFECF_vals(data_dict),
                    'state': 'invoice_sent_failed',
                }

            self.write(document_vals)
        else:
            response_text = response.text
            _logger.error(response_text)
            return

    def _action_update_state_to_dgii(self):
        """Este metodo recoge el resultado de un xml previamente enviado a la DGII y actualiza el documento."""

        ceconfig = self.company_id._filter_ceconfig_by_company()
        env = ceconfig.environment
        if env == 'CerteCF':
            raise UserError(_("This service is not available in this environment (%s)") % env)

        if not self.company_id.vat:
            logging.error(_('Your company has not defined an NIF.'))
            return

        dgii_api = DGIIApi(ceconfig)
        kernel = dgii_api.get_token_semilla()
        if not isinstance(kernel, dict):
            _logger.warning("Token inválido para la empresa '%s': %s", self.company_id.name, kernel)
            return False

        security_code = self.get_security_code()
        response, vals = dgii_api.send_ecf_status_request(
            self.company_id.vat, self.name, self.partner_id.vat, security_code
        )

        if response.status_code == 200:
            if self.l10n_do_ecf_send_state != ECF_STATE_MAP[vals.get('estado')]:
                self.l10n_do_ecf_send_state = ECF_STATE_MAP[vals.get('estado')]
                _logger.info(f"Actualizando estado al ecf: {self.name} a: {ECF_STATE_MAP[vals.get('estado')]}")
        else:
            _logger.error(vals)
            _logger.info('Documento: %s no encontrado en la DGII.', self.name)

    def get_payment_way(self, classdoc=None):
        """ Medios de pagos usados.

                :param object classdoc: Clase del tipo de documento.
                :returns: list
                """
        tabla_forma_pago = classdoc.TablaFormasPago()
        if not self.invoice_id:
            return tabla_forma_pago

        payment_method_id = self.invoice_id.l10n_do_ecf_payment_method
        if payment_method_id and payment_method_id != '0':
            payment_way = classdoc.FormaDePago(FormaPago=int(payment_method_id),
                                               MontoPago=abs(self.xml_amount_total))
            tabla_forma_pago.add_FormaDePago(payment_way)

            return tabla_forma_pago

    def _generate_barcode(self, document_values, xml_file, environment: str):
        """Genera el código QR para el documento electrónico.

            param document_values: diccionario con los valores del documento electrónico.
            param xml_file: archivo XML del documento electrónico.
            param environment: entorno de la DGII (CerteCF, Certificacion, Produccion).

            return: código QR en formato base64.
            """

        self.ensure_one()
        currency = self.currency_id
        data = xml_file
        ecf = ET.fromstring(data)
        signature_value = ecf.findall('{http://www.w3.org/2000/09/xmldsig#}Signature')[0].find(
            '{http://www.w3.org/2000/09/xmldsig#}SignatureValue').text
        code_security = signature_value[0:6]
        date_sign = ecf.findall('FechaHoraFirma')[0].text
        amount_total = abs(currency.round(self.xml_amount_total))
        security_code = code_security

        if self.is_rfce:
            url_params = {
                "RncEmisor": self.company_id.vat,
                "ENCF": self.name,
                "MontoTotal": ("%f" % float(amount_total)).rstrip("0").rstrip("."),
                "CodigoSeguridad": security_code,
            }
            api_url = f'https://fc.dgii.gov.do/{environment}/consultatimbrefc?{urls.url_encode(url_params)}'
        else:
            url_params = {
                "RncEmisor": self.company_id.vat,
                "ENCF": self.name,
                "FechaEmision": self.invoice_id.invoice_date.strftime("%d-%m-%Y"),
                "MontoTotal": ("%s" % amount_total).rstrip("0").rstrip(
                         ".") if self.ncf_type != '43' else (
                             "%f" % abs(self.xml_amount_untaxed_signed)).rstrip("0").rstrip("."),
                "FechaFirma": date_sign,
                "CodigoSeguridad": security_code,
            }
            if self.ncf_type not in ['43', '47']:
                url_params["RncComprador"] = self.partner_id.vat

            api_url = f'https://ecf.dgii.gov.do/{environment}/ConsultaTimbre?{urls.url_encode(url_params)}'

        document_values.update({
            "l10n_do_ecf_security_code": code_security,
            "l10n_do_ecf_sign_date": date_sign,
            "l10n_do_electronic_stamp": api_url,
        })

        # Genera código QR
        qr_code = pyqrcode.create(api_url)
        return qr_code.png_as_base64_str(scale=2)

    def get_security_code(self):
        self.ensure_one()
        if not self.xml_file:
            _logger.warning("Documento '%s' (ID: %s) omitido: campo xml_file vacío.", self.name, self.id)
            return False

        try:
            data = base64.b64decode(self.xml_file)
            if not data.strip():
                _logger.warning("Documento '%s' (ID: %s) omitido: XML vacío tras decodificación.", self.name, self.id)
                return False

            ecf = ET.fromstring(data)
        except Exception as e:
            _logger.warning("Documento '%s' (ID: %s) omitido por error al analizar XML: %s", self.name, self.id, str(e))
            return False

        signature_value = ecf.findall('{http://www.w3.org/2000/09/xmldsig#}Signature')[0].find(
            '{http://www.w3.org/2000/09/xmldsig#}SignatureValue').text
        code_security = signature_value[0:6]
        security_code = code_security
        return security_code

    def _l10n_do_check_documents_for_send(self):
        """ Ensure the current records are eligible for sent to DGII.

                """
        failed_documents = self.filtered(
            lambda o: not (o.company_id._filter_ceconfig_by_company()))
        if failed_documents:
            invoices_str = ", ".join(failed_documents.mapped('name'))
            raise UserError(_("Invoices %s not selected an interface in a company.", invoices_str))

        invoices = self
        return invoices

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
        return self.l10n_latam_document_type_id.doc_code_prefix[1:]

    def get_taxed_amount_data(self):
        """ITBIS taxed amount
        According to the DGII, there are three types of amounts taxed by ITBIS:

        18% -- Most common
        16% -- Used on 'healthy products' like Yogurt, coffee and so on.
        0% -- Should be used on exported products

        See Law No. 253-12, art. 343 of dominican Tributary Code for further info
        """

        itbis_data = {
            "total_taxed_amount": 0,
            "18_taxed_base": 0,
            "18_taxed_amount": 0,
            "16_taxed_base": 0,
            "16_taxed_amount": 0,
            "0_taxed_base": 0,
            "0_taxed_amount": 0,
            "exempt_amount": 0,
            "itbis_withholding_amount": 0,
            "isr_withholding_amount": 0,
            "tax_additional": 0,
            "tax_additional_other": 0,
        }
        lines = []
        if self.invoice_id:
            lines = self.invoice_id._l10n_do_ecf_invoice_line_ids()

        tax_data = [
            line.tax_ids.compute_all(
                price_unit=line.price_subtotal,
                currency=line.currency_id,
                product=line.product_id,
                partner=line.move_id.partner_id,
                handle_price_include=False,
            )
            for line in lines.filtered(lambda l: l.price_unit >= 0)
        ]

        itbis_data["total_taxed_amount"] = sum(
            line["total_excluded"] for line in tax_data
        )
        l10n_do_ncf_type = self.ncf_type
        for line_taxes in tax_data:
            for tax in line_taxes["taxes"]:
                if not tax["amount"] and l10n_do_ncf_type != "46":
                    itbis_data["exempt_amount"] += tax["base"]

                tax_id = self.env["account.tax"].browse(tax["id"])
                if tax_id.amount in [18, 1.8] and l10n_do_ncf_type != "46":
                    itbis_data["18_taxed_base"] += tax["base"]
                    itbis_data["18_taxed_amount"] += tax["amount"]
                elif tax_id.amount == 16 and l10n_do_ncf_type != "46":
                    itbis_data["16_taxed_base"] += tax["base"]
                    itbis_data["16_taxed_amount"] += tax["amount"]
                elif tax_id.amount == 0 and l10n_do_ncf_type == "46":
                    itbis_data["0_taxed_base"] += tax["base"]
                    itbis_data["0_taxed_amount"] += tax["amount"]
                elif tax_id.amount < 0 and tax_id.tax_group_id.l10n_do_billing_indicator == "taxable_itbis":
                    itbis_data["itbis_withholding_amount"] += tax["amount"]
                elif tax_id.amount < 0 and tax_id.tax_group_id.l10n_do_billing_indicator == "taxable_isr":
                    itbis_data["isr_withholding_amount"] += tax["amount"]
                elif tax_id.amount == 10 and tax_id.tax_group_id.l10n_do_billing_indicator == "tips":
                    itbis_data["tax_additional"] += tax["amount"]
                elif tax_id.amount == 17 and tax_id.tax_group_id.l10n_do_billing_indicator == "other":
                    itbis_data["tax_additional_other"] += tax["amount"]
            # Taxes exempt by omission.
            if not line_taxes["taxes"]:
                itbis_data["exempt_amount"] += line_taxes["total_excluded"]

        return itbis_data

    def get_payment_type(self):
        """
        Indicates the type of customer payment. Free delivery invoices (code 3)
        are not valid for Crédito Fiscal.

        1 - Al Contado
        2 - Crédito
        3 - Gratuito
        """
        # TODO: evaluate payment type 3 <Gratuito> Check DGII docs
        if not self.invoice_id.invoice_payment_term_id and self.invoice_id.invoice_date_due:
            if (
                    self.invoice_id.invoice_date_due and self.invoice_id.invoice_date
            ) and self.invoice_id.invoice_date_due > self.invoice_id.invoice_date:
                return 2
            else:
                return 1
        elif not self.invoice_id.invoice_payment_term_id:
            return 1
        elif not self.invoice_id.invoice_payment_term_id == self.env.ref(
                "account.account_payment_term_immediate"
        ):
            return 2
        else:
            return 1

    @api.model
    def _prepare_msg_ECF_vals(self, data_dict: dict):
        response_TrackId = data_dict.get('RespuestaConsultaTrackId')
        message = ("TrackId: " + response_TrackId.get("TrackId") + "\n" +
                   "Codigo: " + response_TrackId.get("Codigo") + "\n" +
                   "Estado: " + response_TrackId.get("Estado") + "\n" +
                   "Mensajes: " + json.dumps(response_TrackId.get("Mensajes"), ensure_ascii=False))
        return message

    @api.model
    def _prepare_msg_RFECF_vals(self, data_dict: dict):
        respuesta = data_dict.get('Respuesta')
        message = ("Codigo: " + respuesta.get("Codigo") + "\n" +
                   "Estado: " + respuesta.get("Estado") + "\n" +
                   "Encf: " + respuesta.get("Encf") + "\n" +
                   "SecuenciaUtilizada: " + respuesta.get("SecuenciaUtilizada") + "\n" +
                   "Mensajes: " + json.dumps(respuesta.get("Mensajes"), ensure_ascii=False))
        return message

    def is_l10n_do_partner(self):
        return self.partner_id.country_id and self.partner_id.country_id == self.env.ref("base.do")

    def is_company_currency(self):
        return self.currency_id == self.company_id.currency_id

    @staticmethod
    def limit(text, limit):
        return (text[:limit - 3] + '...') if len(text) > limit else text

    # ===== CRONs =====

    @api.model
    def cron_ecf_invoices_send_dgii(self, max_doc=10, extra_domain=None):
        """Envia a la DGII los ecf q esten firmados pendientes o sin enviar por error de conexion.

                :param int max_doc:      The maximum size of the batch of documents to process to avoid timeout.
                :param extra_domain:    An optional extra domain to be injected when searching for documents to update.
                """

        domain = [('invoice_id', '!=', False), ('l10n_do_ecf_send_state', 'in', ['signed_pending'])]
        if extra_domain:
            domain = Domain.AND([domain, extra_domain])

        documents = self.search(domain, order='id', limit=max_doc)
        for doc in documents:
            doc.with_context(cron_skip_connection_errs=True)._send_to_dgii()

        self.env.cr.commit()
        _logger.info("##### CRON: ENVIADO ECF A DGII")

    @api.model
    def cron_ecf_invoices_not_sent(self, max_doc=10, extra_domain=None):
        """Envia a la DGII los ecf q tuvieron problemas o error al enviar por conexion. etc.

                :param int max_doc:      The maximum size of the batch of documents to process to avoid timeout.
                :param extra_domain:    An optional extra domain to be injected when searching for documents to update.
        """

        domain = [('invoice_id', '!=', False), ('l10n_do_ecf_send_state', 'in', ['not_sent', 'not_found'])]
        if extra_domain:
            domain = Domain.AND([domain, extra_domain])

        documents = self.search(domain, order='id asc', limit=max_doc)
        for doc in documents:
            doc.with_context(cron_skip_connection_errs=True)._send_to_dgii()

        self.env.cr.commit()
        _logger.info("##### CRON: ENVIADO ECF A DGII")

    @api.model
    def cron_ecf_invoices_pending_send_dgii(self, max_doc=10, extra_domain=None):
        """Busca los ecf q esten en estado 'En proceso' y actualiza su estado."""

        domain = [('invoice_id', '!=', False), ('l10n_do_ecf_send_state', '=', 'delivered_pending')]
        if extra_domain:
            domain = Domain.AND([domain, extra_domain])

        documents = self.search(domain, order='id asc', limit=max_doc)
        for doc in documents:
            doc._action_update_state_to_dgii()

        self.env.cr.commit()
        _logger.info("##### CRON: CONSULTADO ESTADO ECF A DGII")

    def _get_do_document_attachments(self, res_id=None, res_model=None):
        """Crea adjuntos con los archivos CR requeridos (XML generado y XML del MH).

        Args:
            res_id: ID del recurso relacionado (por defecto el ID del documento)
            res_model: Modelo del recurso relacionado (por defecto 'ce.document')

        Returns:
            recordset: ir.attachment recordset con los adjuntos creados
        """
        self.ensure_one()
        ir_attachment = self.env['ir.attachment'].sudo()
        attachments = self.env['ir.attachment']

        # Valores por defecto
        if not res_id:
            res_id = self.id
        if not res_model:
            res_model = self._name

        # Adjunto XML generado
        if self.xml_file:
            attachment_name = str(f"{self.name}.xml")
            attachment_xml = ir_attachment.search([
                ('res_model', '=', res_model),
                ('res_id', '=', res_id),
                ('name', '=', attachment_name),
            ], limit=1)
            if not attachment_xml:
                xml_vals = {
                    'name': attachment_name,
                    'datas': self.xml_file,
                    'res_id': res_id,
                    'res_model': res_model,
                    'type': 'binary',
                }
                attachment_xml = ir_attachment.create(xml_vals)
            attachments |= attachment_xml

        return attachments

    @api.model
    def _send_mail(self, max_mails=10, max_dias=1):
        """Envia email al cliente. De forma masiva (cron) o para un solo registro (Bton Send Email).

                """
        if self:
            documents = self
        else:
            date_origen = datetime.now() - timedelta(days=max_dias)
            documents = self.search([
                ('create_date', '>=', date_origen),
                ('l10n_do_ecf_send_state', 'in', ["delivered_accepted", "conditionally_accepted"]),
                ('state_mail', 'not in', ['sent', 'not_mail'])], limit=max_mails)

        _logger.info('\n\n %r \n\n', documents)
        if not documents:
            return

        email_template = self.env.ref('account.email_template_edi_invoice', False)
        if email_template:
            email_template.attachment_ids = [Command.clear()]
        else:
            _logger.warning('El template de factura de email no existe')
            return

        for doc in documents:
            if doc.invoice_id and doc.partner_id and doc.partner_id.email:
                # # Adjuntos
                attachments = doc._get_do_document_attachments(res_id=doc.id, res_model=self._name)
                attachment_ids = [att.id for att in attachments]

                if attachment_ids:
                    email_template.attachment_ids = [Command.set(attachment_ids)]
                    email_template.subject = "{{ object.company_id.name }} Factura (Ref {{ object.name or 'n/a' }})"
                    (email_template.with_context(type='binary', default_type='binary').
                     send_mail(doc.invoice_id.id, raise_exception=False, force_send=True))

                    # Se eliminan los archivos creados previamente para no generar basura
                    attachments.unlink()
                    email_template.attachment_ids = [Command.clear()]
                    doc.state_mail = 'sent'
                    doc.message_post(subject='Email', body='Factura enviada')
            else:
                doc.state_mail = 'not_mail'
                doc.message_post(subject='Email', body='Factura No enviada, la empresa no tiene email')


class ECFReference(models.Model):
    _name = 'ecf.reference'
    _description = 'ECF Reference'

    name = fields.Char()
    ref_number = fields.Char(string='Reference Number', required=True)
    ref_date = fields.Datetime(string='Reference Creation Date', required=True)
    ref_reason = fields.Char(string='Reference Reason', required=True)
    company_id = fields.Many2one('res.company', string='Company', required=True)

    def action_view_document_reference(self):
        self.ensure_one()
        ref_number = self.ref_number
        return {
            'type': 'ir.actions.act_window',
            'name': _('Document Reference'),
            'res_model': 'ecf.document',
            'view_mode': 'list,form',
            'domain': [('name', '=', ref_number)],
        }

    def action_download_file(self):
        """ Download the XML file linked to the document.

        :return: An action to download the attachment.
        """
        self.ensure_one()
        reference_id = self.env["ecf.document"].search([('name', '=', self.ref_number)], limit=1)
        return {
            'type': 'ir.actions.act_url',
            'url': f'/web/content/ecf.document/{reference_id.id}/xml_file/?download=true&filename={reference_id.xml_file_name}',
        }
