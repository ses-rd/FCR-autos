# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from lxml import etree

parser = etree.XMLParser(remove_blank_text=True)


class ResCompany(models.Model):
    _inherit = 'res.company'

    commercial_name = fields.Char("Commercial Name")
    ecf_config = fields.Many2one('ecf.settings', string='Electronic Voucher Setting')

    def _filter_ceconfig_by_company(self):
        """ Filter interfaces by the given company
            It goes through the company hierarchy until a tax is found
        """
        if not self:
            return self
        company_id = self
        ceconfig, company = self.env['ecf.settings'], company_id
        while not ceconfig and company:
            ceconfig = self.ecf_config.filtered(lambda t: t.company_id == company)
            company = company.sudo().parent_id
        return ceconfig
