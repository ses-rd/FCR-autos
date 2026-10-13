from odoo import models, fields, http, api
from odoo.http import request
import base64
import logging
import os

class ResCompany(models.Model):
    _inherit = 'res.company'

    seal = fields.Binary(string="Company Seal")
