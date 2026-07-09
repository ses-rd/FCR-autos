from odoo import models, fields, api


class FleetCreateProductWizard(models.TransientModel):
    _name = "fleet.create.product.wizard"
    _description = "Create Product from Fleet Vehicle"

    vehicle_id = fields.Many2one(comodel_name="fleet.vehicle")
    name = fields.Char(string="Product Name")
    categ_id = fields.Many2one(comodel_name="product.category", string="Product Category")
    type = fields.Selection([('consu', 'Consumable'), ('service', 'Service'), ('combo', 'Combo')],
                            default='consu')
    uom_id = fields.Many2one(comodel_name="uom.uom", string="Unit of Measure")

    @api.model
    def default_get(self, fields_list):
        res = super().default_get(fields_list)
        vehicle_id = self.env['fleet.vehicle'].browse(self.env.context.get('default_vehicle_id'))
        if vehicle_id:
            res['name'] = vehicle_id.name
        unit_uom_id = self.env.ref('uom.product_uom_unit', raise_if_not_found=False)
        if unit_uom_id:
            res['uom_id'] = unit_uom_id.id
        return res

    def action_create_product(self):
        product_tmpl_id = self.env['product.template'].create({
            'name': self.name,
            'categ_id': self.categ_id.id,
            'type': self.type,
            'uom_id': self.uom_id.id,
            'default_code': self.vehicle_id.license_plate,
            'is_fleet': True,
            'vehicle_id': self.vehicle_id.id,
            'is_storable': True,
        })
        self.vehicle_id.product_tmpl_id = product_tmpl_id.id
        self.vehicle_id.product_id = product_tmpl_id.product_variant_id.id

        return {
            'type': 'ir.actions.act_window',
            'res_model': 'product.template',
            'view_mode': 'form',
            'res_id': product_tmpl_id.id,
        }
