# -*- coding: utf-8 -*-
from odoo import models, fields, api


class State(models.Model):
    _inherit = 'res.country.state'

    ecf_code = fields.Char(string="ECF code", size=6)

    @api.model
    def _name_search(self, search_value, args=None, operator='ilike', limit=100, order=None):
        """ search in name, code and category"""
        args = args or []
        # search in name and ecf_code
        domain = args + ['|', ('name', operator, search_value),
                         ('ecf_code', operator, search_value)]
        return self._search(domain, limit=limit, order=order)
