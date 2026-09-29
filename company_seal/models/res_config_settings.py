from odoo import models, fields, http, api


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    company_seal = fields.Binary(related='company_id.seal', string="Company Seal", readonly=False)
