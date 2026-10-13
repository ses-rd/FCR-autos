from odoo import models, fields, http, api
from odoo.http import request
import base64
import logging
import os

_logger = logging.getLogger(__name__)


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    company_seal = fields.Binary(related='company_id.seal', string="Company Seal", readonly=False)

    # @api.model_create_multi
    # def create(self, vals_list):
    #     for vals in vals_list:
    #         if not vals.get('company_seal'):
    #             # Establecer un valor predeterminado para company_seal
    #             vals['company_seal'] = self._get_default_seal()
    #     return super(ResConfigSettings, self).create(vals_list)
    #
    # def write(self, vals):
    #     if not vals.get('company_seal') or not vals['company_seal']:
    #         # Establecer un valor predeterminado para company_seal si está vacío
    #         vals['company_seal'] = self._get_default_seal()
    #     return super(ResConfigSettings, self).write(vals)
    #
    # def _get_default_seal(self):
    #     # Aquí puedes definir el valor predeterminado para el sello de la empresa
    #     # Por ejemplo, puedes cargar una imagen predeterminada desde un archivo
    #     try:
    #         module_path = os.path.dirname(os.path.abspath(__file__))
    #         image_path = os.path.join(module_path, '../static/img/default_seal.png')
    #         with open(image_path, 'rb') as f:
    #             return base64.b64encode(f.read())
    #     except Exception as e:
    #         _logger.error("Error al cargar el sello predeterminado: %s", e)
    #         return False
