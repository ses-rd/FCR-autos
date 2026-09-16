from odoo import _, fields, models
from odoo.exceptions import UserError
from odoo.tools.misc import format_date


class StockPicking(models.Model):
    _inherit = 'stock.picking'

    def _get_vehicle_conduce_moves(self):
        """Use this transfer only; ignore cancelled and zero-quantity moves."""
        self.ensure_one()
        return self.move_ids.filtered(
            lambda move: move.state != 'cancel'
            and (move.quantity if self.state == 'done' else move.product_uom_qty) > 0
        )

    def _get_vehicle_conduce_date(self):
        """Effective date for done transfers, scheduled date for ready transfers."""
        self.ensure_one()
        if self.state not in ('assigned', 'done'):
            raise UserError(_(
                'La transferencia %(picking)s debe estar Lista o Hecha para imprimir el conduce.',
                picking=self.display_name,
            ))
        date = self.date_done if self.state == 'done' else self.scheduled_date
        if not date:
            raise UserError(_(
                'La transferencia %(picking)s no tiene la fecha efectiva o programada requerida.',
                picking=self.display_name,
            ))
        return date

    def _get_vehicle_conduce_vehicle(self, moves):
        """Resolve Fleet through each moved product's template, never through SO lines."""
        self.ensure_one()
        products = moves.product_id
        missing = products.filtered(
            lambda product: product.product_tmpl_id.is_fleet
            and not product.product_tmpl_id.vehicle_id
        )
        if missing:
            raise UserError(_(
                'Hay productos marcados como vehículo sin vínculo con Fleet en %(picking)s: %(products)s.',
                picking=self.display_name,
                products=', '.join(missing.mapped('display_name')),
            ))
        vehicles = products.product_tmpl_id.vehicle_id
        if not vehicles:
            raise UserError(_(
                'No hay un vehículo de Fleet asociado a los productos de la transferencia %(picking)s.',
                picking=self.display_name,
            ))
        if len(vehicles) != 1:
            raise UserError(_(
                'La transferencia %(picking)s contiene varios vehículos (%(vehicles)s). '
                'El Conduce de Salida requiere exactamente un vehículo.',
                picking=self.display_name,
                vehicles=', '.join(vehicles.mapped('display_name')),
            ))
        vehicle = vehicles
        vehicle_products = products.filtered(
            lambda product: product.product_tmpl_id.vehicle_id == vehicle
        )
        if len(vehicle_products) != 1:
            raise UserError(_(
                'Varios productos de %(picking)s apuntan al mismo vehículo. '
                'Corrija el vínculo producto–vehículo antes de imprimir.',
                picking=self.display_name,
            ))
        product = vehicle_products
        if (
            (vehicle.product_id and vehicle.product_id != product)
            or (vehicle.product_tmpl_id and vehicle.product_tmpl_id != product.product_tmpl_id)
        ):
            raise UserError(_(
                'El vínculo entre el producto y el vehículo %(vehicle)s es contradictorio. '
                'Revise los productos vinculados en Fleet.',
                vehicle=vehicle.display_name,
            ))
        if not vehicle.active or (vehicle.company_id and vehicle.company_id != self.company_id):
            raise UserError(_(
                'El vehículo %(vehicle)s está archivado o pertenece a otra compañía.',
                vehicle=vehicle.display_name,
            ))
        return vehicle

    def _get_vehicle_conduce_outgoing_values(self):
        """Validate business rules even when rendering directly or in a mixed batch."""
        self.ensure_one()
        if self.picking_type_code != 'outgoing':
            raise UserError(_(
                'El Conduce de Salida solo corresponde a operaciones de salida: %(picking)s.',
                picking=self.display_name,
            ))
        date = self._get_vehicle_conduce_date()
        moves = self._get_vehicle_conduce_moves()
        sales = moves.sale_line_id.order_id
        if not self.sale_id or not sales:
            raise UserError(_(
                'La transferencia %(picking)s no está vinculada a una venta mediante sus movimientos.',
                picking=self.display_name,
            ))
        if len(sales) != 1 or sales != self.sale_id:
            raise UserError(_(
                'La transferencia %(picking)s tiene relaciones de venta ambiguas o contradictorias.',
                picking=self.display_name,
            ))
        sale = sales
        if sale.company_id != self.company_id:
            raise UserError(_('La venta y la transferencia deben pertenecer a la misma compañía.'))
        vehicle = self._get_vehicle_conduce_vehicle(moves)
        vehicle_moves = moves.filtered(
            lambda move: move.product_id.product_tmpl_id.vehicle_id == vehicle
        )
        if any(
            move.sale_line_id.order_id != sale
            or move.sale_line_id.product_id != move.product_id
            for move in vehicle_moves
        ):
            raise UserError(_(
                'Los movimientos del vehículo en %(picking)s deben estar vinculados '
                'a líneas del mismo producto en la venta correspondiente.',
                picking=self.display_name,
            ))
        partner = self.partner_id or sale.partner_shipping_id or sale.partner_id
        if not partner:
            raise UserError(_('No se encontró el contacto destinatario de la entrega.'))
        # Category is the closest existing field to SUV/pickup/etc.; fall back to car/bike.
        vehicle_type = vehicle.category_id.name or dict(
            vehicle._fields['vehicle_type']._description_selection(self.env)
        ).get(vehicle.vehicle_type, '')
        return {
            'picking': self,
            'company': self.company_id,
            'sale': sale,
            'partner': partner,
            'vehicle': vehicle,
            'vehicle_type': vehicle_type,
            'odometer_unit': {'kilometers': 'km', 'miles': 'mi'}.get(vehicle.odometer_unit, ''),
            'date': format_date(
                self.env, fields.Datetime.context_timestamp(self, date).date(),
                date_format='dd/MM/yyyy',
            ),
        }
