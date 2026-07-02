# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import UserError
from ..dgii_api import DGII_VERSION
from . import ACECF
from lxml import etree
from ..dgii_api import DGIIApi
import subprocess
import tempfile
import base64
import logging
import json
import xmltodict

_logger = logging.getLogger(__name__)
parser = etree.XMLParser(remove_blank_text=True)

ACECF_STATE_MAP = {
    "Aprobacion Comercial Rechazada.": "reject",
    "Aprobacion Comercial Aprobada.": "accepted",
}


class ACECFDocument(models.Model):
    _name = 'acecf.document'
    _description = 'ACECF Document'
    _inherit = ["portal.mixin", "mail.thread"]
    _order = "date_issue desc, id desc"

    name = fields.Char(string='e-NCF', readonly=True)
    invoice_id = fields.Many2one('account.move', string='Invoice', ondelete='cascade', readonly=True,
                                 required=True, index=True)
    company_id = fields.Many2one('res.company', string='Company', required=True)
    company_currency_id = fields.Many2one(
        string='Company Currency',
        related='company_id.currency_id', readonly=True,
    )
    currency_id = fields.Many2one('res.currency', readonly=True, string='Currency')
    partner_id = fields.Many2one('res.partner', string='Partner', readonly=True)
    xml_amount_total = fields.Monetary('Amount Total')

    # Commercial Approved
    xml_commercial_approval_file = fields.Binary(attachment=True, string="Commercial Approval File", copy=False,
                                                 help="This field holds the XML file generated and signed by system")
    xml_commercial_approval_file_name = fields.Char("Name of XML Commercial Approval File")
    xml_dgii_acecf_file = fields.Binary(string="XML ACECF DGII File", attachment=True, copy=False)
    xml_dgii_acecf_file_name = fields.Char(string="Nombre Archivo XML", copy=False)
    message_detail_dgii_acecf = fields.Text(string="Message Detail DGII ACECF", copy=False)
    customer_decision = fields.Selection([('pending', 'Pending'),
                                          ('accepted', 'Accepted'),
                                          ('system_accepted', 'System Approved'),
                                          ('reject', 'Reject')],
                                         default='pending', tracking=True)
    date_acknowledgment = fields.Datetime(readonly=True)
    l10n_do_acecf_send_state = fields.Selection(selection=[('pending', 'Pending'),
                                                           ('accepted', 'Accepted'),
                                                           ('reject', 'Reject')],
                                                string="ACECF Send State", copy=False, required=True, readonly=True,
                                                default="pending", tracking=True)
    reject_reason = fields.Text()
    date_issue = fields.Date(string="Fecha emisión del documento", copy=False)
    invoice_date = fields.Date(copy=False)
    state_inv_supplier = fields.Selection(
        [('1', 'Aceptado'),
         ('2', 'Rechazado'),
         ], string="Respuesta cliente", default="1")
    response_status_code = fields.Text()
    state = fields.Selection(
        selection=[
            ('invoice_sent', "Sent"),
            ('invoice_sent_failed', "Send In Error"),
        ],
        required=False,
    )
    retry_button_needed = fields.Boolean(compute='_compute_retry_button_needed')

    # === COMPUTE METHODS ===#

    @api.depends('state', 'xml_commercial_approval_file')
    def _compute_retry_button_needed(self):
        """ Compute whatever or not the 'retry' button should be displayed. """
        doc_state_mapping = self._get_retry_button_map()
        for doc in self:
            results = doc_state_mapping.get(doc.state)
            doc.retry_button_needed = bool(results) and (not results[0] or results[0](doc))

    def _action_gen_xml_ACECF(self):
        self.ensure_one()
        ceconfig = self.company_id._filter_ceconfig_by_company()
        cedoc = self._gen_acefc_doc()
        file = tempfile.NamedTemporaryFile(delete=False)
        file.write(b'<?xml version="1.0" encoding="utf-8"?>')
        cedoc.export(file, 0, namespacedef_="", pretty_print=False)
        file.write(b'\n')
        file.close()
        xml_name = "{}.xml".format((self.partner_id.vat or '') + self.name)
        args = 'mv ' + file.name
        args = args.split()
        signed_filename = "/tmp/" + xml_name
        args.append(signed_filename)
        subprocess.run(args)
        xml_f = open(signed_filename, 'rb')
        xml_file = xml_f.read()
        dgii_api = DGIIApi(ceconfig)
        xml_encoded = bytes(xml_file)
        subprocess.call(['rm', '-f', signed_filename])
        try:
            _xml = etree.XML(xml_encoded, parser=parser)
            xml_signed = dgii_api.generate_signature(_xml)
        except Exception as e:
            raise UserError('Error al firmar. Compruebe las credenciales.')

        xml_f.close()
        return (xml_signed, xml_name)

    def _gen_acefc_doc(self):
        """ Retorna la instancia del elemento raiz de ACECF.

            :returns: obj de AprobacionComercial
            """

        now = fields.Datetime.context_timestamp(
            self.with_context(tz="America/Santo_Domingo"),
            fields.Datetime.now(),
        ).strftime("%d-%m-%Y %H:%M:%S")

        version = DGII_VERSION
        state = self.state_inv_supplier
        detalle_aprobacion_comercial = ACECF.DetalleAprobacionComercial(Version=version,
                                                                        RNCEmisor=self.partner_id.vat,
                                                                        eNCF=self.name,
                                                                        FechaEmision=self.invoice_date,
                                                                        MontoTotal=self.xml_amount_total,
                                                                        RNCComprador=self.company_id.vat,
                                                                        Estado=int(state),
                                                                        FechaHoraAprobacionComercial=now,
                                                                        )
        if self.state_inv_supplier == '2' and self.reject_reason:
            detalle_aprobacion_comercial.set_DetalleMotivoRechazo(self.reject_reason)

        return ACECF.AprobacionComercial(DetalleAprobacionComercial=detalle_aprobacion_comercial)

    def send_ACECF(self):
        """Envia un xml de Aprobacion Comercial a la DGII."""

        company_id = self.company_id
        ceconfig = company_id._filter_ceconfig_by_company()
        if not ceconfig:
            msg = _("Must be selected an Environment in a Company.")
            _logger.error(msg)
            return False

        dgii_api = DGIIApi(ceconfig)
        xml_signed, xml_name = self._action_gen_xml_ACECF()
        response, vals = dgii_api.send_commercial_approved(xml_signed, xml_name)
        self.response_status_code = response.status_code
        if response.status_code in (200, 400):
            data_dict = xmltodict.parse(vals)
            _logger.info(data_dict)
            l10n_do_acecf_send_state = ACECF_STATE_MAP[data_dict.get('RespuestaAprobacionComercial').get('Estado')]
            document_vals = {
                'l10n_do_acecf_send_state': l10n_do_acecf_send_state,
                'xml_dgii_acecf_file_name': 'ACECF_%s.xml' % self.name,
                'xml_dgii_acecf_file': base64.b64encode(bytes(vals.encode('utf-8'))),
                'message_detail_dgii_acecf': self._prepare_msg_ACECF_vals(data_dict),
                'xml_commercial_approval_file': base64.b64encode(xml_signed),
                'xml_commercial_approval_file_name': xml_name,
            }
            if l10n_do_acecf_send_state == 'reject':
                document_vals['state'] = 'invoice_sent_failed'
            else:
                document_vals['state'] = 'invoice_sent'

            self.write(document_vals)

    def _prepare_msg_ACECF_vals(self, data_dict):
        response_ac = data_dict.get('RespuestaAprobacionComercial')
        message = ("Codigo: " + response_ac.get("Codigo") + "\n" +
                   "Estado: " + response_ac.get("Estado") + "\n" +
                   "Mensajes: " + json.dumps(response_ac.get("Mensaje")))
        return message

    def action_download_file(self):
        """ Download the XML file linked to the document.

        :return: An action to download the attachment.
        """
        self.ensure_one()
        document_id = self
        return {
            'type': 'ir.actions.act_url',
            'url': f'/web/content/{self._name}/{document_id.id}/xml_commercial_approval_file/?download=true&filename={document_id.xml_commercial_approval_file_name}',
        }

    def action_show_document(self):
        """ View the record(s) owning this document. """
        self.ensure_one()

        return {
            'name': _("Invoice"),
            'type': 'ir.actions.act_window',
            'res_model': self._name,
            'view_mode': 'list,form',
            'domain': [('id', 'in', self.ids)],
            'context': {'create': False},
        }

    def action_retry(self):
        """ Retry the current document. """
        self.ensure_one()
        self._get_retry_button_map()[self.state][1](self)

    @api.model
    def _get_retry_button_map(self):
        """ Mapping to manage the 'retry' flow on documents.

        :return: A mapping:
            <source_state>: (<extra_condition_function>, <retry_function>)
            where:
                <source_state>  is the original state of the document allowing a retry flow
                                (a.k.a any failing document such as 'invoice_sent_failed').
                <extra_condition_function>  is an optional function allowing extra checking on the document (mainly specific stuff
                                            depending on the related business record owning the document).
                <retry_function>    is the function to be called when clicking on the 'retry' button.
        """
        return {
            'invoice_sent_failed': (
                None,
                lambda x: x._action_retry_invoice_try_send(),
            ),
            # 'invoice_cancel_failed': (
            #     None,
            #     lambda x: x._action_retry_invoice_try_cancel(),
            # ),
            # 'invoice_cancel_requested_failed': (
            #     None,
            #     lambda x: x._action_retry_invoice_try_cancel(),
            # ),
        }

    def _action_retry_invoice_try_send(self):
        """ Retry the sending of an invoice ACECF document that failed to be sent. """
        self.ensure_one()
        # records = self._get_source_records()
        if self.invoice_id:
            self.invoice_id.l10n_do_acecf_invoice_retry_send()
