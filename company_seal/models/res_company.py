from odoo import models, fields, http, api


class ResCompany(models.Model):
    _inherit = 'res.company'

    seal = fields.Binary(string="Company Seal")
