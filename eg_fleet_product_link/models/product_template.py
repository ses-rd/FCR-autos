from odoo import models, fields


class ProductTemplate(models.Model):
    _inherit = "product.template"

    is_fleet = fields.Boolean(string="Is Fleet", copy=False)
    vehicle_id = fields.Many2one(comodel_name="fleet.vehicle", string="Vehicle", copy=False)
    license_plate = fields.Char(related="vehicle_id.license_plate", string="License Plate")
    model_id = fields.Many2one(related="vehicle_id.model_id", string="Model")
