# -*- coding: utf-8 -*-

from odoo import models, fields, api, tools, _
from datetime import datetime
from base64 import b64decode
from cryptography.x509.oid import NameOID
from cryptography.hazmat.primitives.serialization.pkcs12 import load_key_and_certificates
from ..dgii_api import DGIIApi
from odoo.exceptions import ValidationError, UserError

import logging
_logger = logging.getLogger(__name__)


class ECFSettings(models.Model):
    _name = 'ecf.settings'
    _description = 'Electronic Vouchers Configuration'

    name = fields.Char(required=True)
    environment = fields.Selection([
        ('CerteCF', 'Certification'),
        ('TesteCF', 'Pre-certification'),
        ('eCF', "Production"),
    ], default='TesteCF', required=True)
    ce_p12_pin = fields.Char(string='p12 pin', required=True)
    ce_p12_file = fields.Binary("Certificate file", required=True)
    ce_p12_name = fields.Char("Name of certificate file")
    company_id = fields.Many2one("res.company", string="Company", ondelete='cascade', readonly=True)
    state = fields.Selection(
        [
            ("unverified", "Unverified"),
            ("valid", "Valid Signature"),
            ("expired", "Signature Expired"),
        ],
        default="unverified",
        readonly=True,
    )

    # datos informativos del certificado
    issue_date = fields.Date(string="Date Issue", readonly=True)
    expire_date = fields.Date(string="Expiration date", readonly=True)
    subject_serial_number = fields.Char(string="Serial Number(Subject)", readonly=True)
    subject_common_name = fields.Char(string="Organization (Subject)", readonly=True)
    issuer_common_name = fields.Char(string="Organization (Issuer)", readonly=True)
    cert_serial_number = fields.Char(
        string="Serial number (certificate)", readonly=True
    )
    cert_version = fields.Char(string="Version", readonly=True)
    days_for_notification = fields.Integer(string="Days for notification", default=30)

    # token info
    access_token = fields.Char('Session Access token')
    access_token_expires_in = fields.Datetime('Access token expires in')

    def action_verify(self):
        self.ensure_one()
        dgii_api = DGIIApi(self)
        kernel = dgii_api.get_token_semilla()
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'type': 'info',
                'sticky': False,
                'message': "%s" % kernel,
            }
        }

    def _decode_certificate(self):
        self.ensure_one()
        if not self.ce_p12_pin:
            return None, None
        file_content = b64decode(self.ce_p12_file)
        try:
            private_key, cert, additional_certs = load_key_and_certificates(file_content,
                                                                            self.ce_p12_pin.encode())

        except Exception as ex:
            _logger.warning(tools.ustr(ex))
            raise UserError(
                _(
                    "Error opening the signature, possibly the signature key has "
                    "been entered incorrectly or the file is not supported. \n%s"
                )
                % (tools.ustr(ex))
            ) from None
        return private_key, cert

    def action_validate_and_load(self):
        _private_key, cert = self._decode_certificate()
        issuer = cert.issuer
        subject = cert.subject
        subject_common_name = (
            subject.get_attributes_for_oid(NameOID.COMMON_NAME)[0].value
            if subject.get_attributes_for_oid(NameOID.COMMON_NAME)
            else ""
        )
        subject_serial_number = (
            subject.get_attributes_for_oid(NameOID.SERIAL_NUMBER)[0].value
            if subject.get_attributes_for_oid(NameOID.SERIAL_NUMBER)
            else ""
        )
        issuer_common_name = (
            issuer.get_attributes_for_oid(NameOID.COMMON_NAME)[0].value
            if subject.get_attributes_for_oid(NameOID.COMMON_NAME)
            else ""
        )
        vals = {
            "issue_date": cert.not_valid_before,
            "expire_date": cert.not_valid_after,
            "subject_common_name": subject_common_name,
            "subject_serial_number": subject_serial_number,
            "issuer_common_name": issuer_common_name,
            "cert_serial_number": cert.serial_number,
            "cert_version": cert.version,
            "state": "valid",
        }
        self.write(vals)
        return True

    def days_to_expire(self):
        if self.expire_date:
            return (self.expire_date - fields.Date.context_today(self)).days
        return 0

    def _validate_expiration_certificate(self):
        ceconfig = self
        if ceconfig.state == 'expired':
            msg = _("Certificate is expired.")
            raise ValidationError(msg)
        if ceconfig.state == 'valid' and (0 < ceconfig.days_to_expire() <= 0):
            "Si el certificado esta verificado y los dias restante de vencimiento es 0."
            ceconfig.write({'state': 'expired'})
            msg = _("Certificate days to expired.")
            raise ValidationError(msg)

    def _sign(self, dgii_api, xml_encoded):
        """ Compute and return the message's signature.

        :param HaciendaApi hacienda_api: An instance HaciendaApi
        :param byte xml_encoded: The xml to sign.

        :return: The formatted signature bytes of the message
        :rtype: bytes
        """

        self.ensure_one()
        self._validate_expiration_certificate()
        if not self.ce_p12_file:
            raise UserError(_("No private key linked to the certificate, it is required to sign documents."))
        if not self.ce_p12_pin:
            raise UserError(_("No PIN linked to the certificate, it is required to sign documents."))

        return dgii_api.generate_signature(xml_encoded)

    def set_token_data(self, token_data: dict):
        self.ensure_one()
        expire = datetime.strptime(token_data.get('expira'), "%Y-%m-%dT%H:%M:%SZ")
        self.write({
            'access_token': token_data.get('access_token'),
            'access_token_expires_in': expire
        })

    def clear_token_cache(self):
        self.ensure_one()
        self.write({
            'access_token': False,
            'access_token_expires_in': False
        })
