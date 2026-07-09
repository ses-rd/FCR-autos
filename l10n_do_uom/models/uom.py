# -*- coding: utf-8 -*-
from odoo import api, fields, models, _


class UOM(models.Model):
    _inherit = "uom.uom"

    ecf_code = fields.Char(string="e-CF Code", size=2, help="DGII Code")
