# -*- coding: utf-8 -*-

from odoo import api, _, models, fields


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    is_marbete = fields.Boolean(string="Is Marbate Product")
    is_first_registration = fields.Boolean(string="Is First Registration")
