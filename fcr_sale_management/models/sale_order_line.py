# -*- coding: utf-8 -*-
from odoo import api, fields, models


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    brand = fields.Char(string="Marca")
    model = fields.Char(string="Modelo")
    color = fields.Char(string="Color")
    registration = fields.Char(string="Placa")
