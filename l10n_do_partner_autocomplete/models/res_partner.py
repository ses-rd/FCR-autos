# -*- coding: utf-8 -*-
import re
import lxml.html
import requests
from odoo import models, fields, api, _
from odoo.exceptions import UserError


class Partner(models.Model):
    _inherit = "res.partner"

    @api.onchange("vat", "country_id")
    def _check_rnc(self):
        for partner_rnc in self:
            dgii_autocomplete = self.env['ir.config_parameter'].sudo(
            ).get_param('l10n_do_partner_autocomplete.dgii_autocomplete', False)

            is_dominican_partner = bool(partner_rnc.country_id == self.env.ref("base.do"))
            if (
                    partner_rnc.vat
                    and is_dominican_partner
            ):
                if (
                        len(partner_rnc.vat) not in [9, 11]
                ):
                    raise UserError(
                        _(
                            "Check Vat Format or should not have any Caracter like '-'"
                        )
                    )
                else:

                    if dgii_autocomplete:
                        url = 'https://dgii.gov.do/app/WebApps/ConsultasWeb2/ConsultasWeb/consultas/rnc.aspx'
                        session = requests.Session()
                        session.headers.update({
                            'User-Agent': 'Mozilla/5.0 (python-stdnum)',
                        })

                        document = lxml.html.fromstring(
                            session.get(url, timeout=30, verify=False).text)

                        validation = document.find('.//input[@name="__EVENTVALIDATION"]').get('value')
                        viewstate = document.find('.//input[@name="__VIEWSTATE"]').get('value')
                        data = {
                            '__EVENTVALIDATION': validation,
                            '__VIEWSTATE': viewstate,
                            'ctl00$cphMain$btnBuscarPorRNC': 'Buscar',
                            'ctl00$cphMain$txtRNCCedula': partner_rnc.vat,
                        }
                        # Do the actual request
                        document = lxml.html.fromstring(
                            session.post(url, data=data, timeout=30, verify=False).text)

                        result = document.find('.//div[@id="cphMain_divBusqueda"]')
                        message = document.findtext('.//*[@id="cphMain_lblInformacion"]')

                        if result is not None:
                            hearder = []
                            keys = []

                            for x in result.findall('.//tr/td'):
                                if x.attrib:
                                    hearder.append(x.text.strip())
                                else:
                                    keys.append(x.text.strip())

                            if message:
                                data = {
                                    'validation_message': message.strip(),
                                }
                            else:
                                data = {
                                    'validation_message': 'Cédula/RNC es Válido',
                                }

                            data.update(zip(hearder, keys))

                            info = self._convert_result(data)

                            if "name" in info:
                                info["name"] = " ".join(
                                    re.split(r"\s+", info["name"], flags=re.UNICODE))

                                partner_rnc.name = info["name"]

                            # Agregar Actividad Económica a la nota interna
                            if "activity" in info:
                                partner_rnc.comment = (partner_rnc.comment or "") + "\nActividad Económica: " + info[
                                    "activity"]

                            # Agregar etiqueta de Estado
                            if "status" in info:
                                status_tag_name = f"Estado-{info['status']}"
                                existing_tag = self.env['res.partner.category'].search([('name', '=', status_tag_name)],
                                                                                       limit=1)
                                if not existing_tag:
                                    existing_tag = self.env['res.partner.category'].create({'name': status_tag_name})
                                if existing_tag not in partner_rnc.category_id:
                                    partner_rnc.category_id = [(4, existing_tag.id)]

                            # Agregar etiqueta de Régimen de pagos
                            if "type" in info:
                                type_tag_name = f"Régimen de pagos-{info['type']}"
                                existing_tag = self.env['res.partner.category'].search([('name', '=', type_tag_name)],
                                                                                       limit=1)
                                if not existing_tag:
                                    existing_tag = self.env['res.partner.category'].create({'name': type_tag_name})
                                if existing_tag not in partner_rnc.category_id:
                                    partner_rnc.category_id = [(4, existing_tag.id)]

    def _convert_result(self, result):  # pragma: no cover
        """Translate SOAP result entries into dictionaries."""
        translation = {
            u'Cédula/RNC': 'rnc',
            u'Nombre Comercial': 'commercial_name',
            u'Régimen de pagos': 'type',
            u'Categoría': "category",
            u'Nombre/Razón Social': 'name',
            'Estado': 'status',
            u'Actividad Economica': 'activity',
            u'Administracion Local': 'local_place',

        }
        return dict(
            (translation.get(key, key), value)
            for key, value in result.items())
