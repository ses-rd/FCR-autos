from odoo import models, fields, api


class FleetVehicle(models.Model):
    _inherit = "fleet.vehicle"

    product_tmpl_id = fields.Many2one(comodel_name="product.template", string="Product", copy=False)
    product_id = fields.Many2one(comodel_name="product.product", string="Product", copy=False)
    stock_quant_count = fields.Float(compute="_compute_stock_quant_count")
    nbr_moves_in = fields.Integer(compute="_compute_move_counts", string="Incoming")
    nbr_moves_out = fields.Integer(compute="_compute_move_counts", string="Outgoing")

    def _compute_stock_quant_count(self):
        for rec in self:
            if rec.product_id:
                quant_ids = self.env['stock.quant'].search([('product_id', '=', rec.product_id.id),
                                                            ('location_id.usage', '=', 'internal')])
                rec.stock_quant_count = sum(quant_ids.mapped('quantity'))
            else:
                rec.stock_quant_count = 0

    def _compute_move_count(self):
        for rec in self:
            if rec.product_id:
                move_ids = self.env['stock.move'].search([('product_id', '=', rec.product_id.id)])
                rec.move_count = len(move_ids)
            else:
                rec.move_count = 0

    def action_create_product(self):
        return {'name': 'Create Fleet Product',
                'type': 'ir.actions.act_window',
                'res_model': 'fleet.create.product.wizard',
                'view_mode': 'form',
                'target': 'new',
                'context': {'default_vehicle_id': self.id}
                }

    def action_view_product_template(self):
        return {'type': 'ir.actions.act_window',
                'name': 'Product',
                'res_model': 'product.template',
                'view_mode': 'form',
                'res_id': self.product_tmpl_id.id, }

    def action_view_stock_quants(self):
        return {'type': 'ir.actions.act_window',
                'name': 'Stock On Hand',
                'res_model': 'stock.quant',
                'view_mode': 'list,form',
                'domain': [('product_id', '=', self.product_id.id), ('location_id.usage', '=', 'internal')],
                }

    def action_view_stock_move_lines(self):
        self.ensure_one()
        return {"type": "ir.actions.act_window",
                "name": "Stock Move Lines",
                "res_model": "stock.move.line",
                "view_mode": "list,form",
                "domain": [('product_id', '=', self.product_id.id),
                           '|',
                           ('location_id.usage', '=', 'internal'),
                           ('location_dest_id.usage', '=', 'internal')],
                }

    def _compute_move_counts(self):
        for rec in self:
            if rec.product_id:
                rec.nbr_moves_in = self.env['stock.move.line'].search_count([
                    ('product_id', '=', rec.product_id.id), ('location_dest_id.usage', '=', 'internal')])
                rec.nbr_moves_out = self.env['stock.move.line'].search_count([
                    ('product_id', '=', rec.product_id.id), ('location_id.usage', '=', 'internal')])
            else:
                rec.nbr_moves_in = 0
                rec.nbr_moves_out = 0
