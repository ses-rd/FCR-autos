# -*- coding: utf-8 -*-

from odoo import api, _, models, fields
from odoo.exceptions import ValidationError


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    is_marbete = fields.Boolean(string="Is Marbate Product")
