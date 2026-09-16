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

    def _get_vehicle_conduce_vehicle(self, moves, document_name):
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
                '%(document_name)s requiere exactamente un vehículo.',
                picking=self.display_name,
                vehicles=', '.join(vehicles.mapped('display_name')),
                document_name=document_name,
            ))
        vehicle = vehicles
        # Fleet's product_id/product_tmpl_id are independent, unsynchronised fields.
        # They are not an inverse of product.template.vehicle_id and may be stale.
        # Multiple products pointing to this same record do not make it ambiguous.
        # Archived vehicles remain valid for reprinting historical transfers.
        if vehicle.company_id and vehicle.company_id != self.company_id:
            raise UserError(_(
                'El vehículo %(vehicle)s pertenece a otra compañía.',
                vehicle=vehicle.display_name,
            ))
        return vehicle

    def _get_vehicle_conduce_type(self, vehicle):
        """Provisional body/type label: existing category, then car/bike label."""
        self.ensure_one()
        vehicle.ensure_one()
        return vehicle.category_id.name or dict(
            vehicle._fields['vehicle_type']._description_selection(self.env)
        ).get(vehicle.vehicle_type, '')

    def _get_vehicle_conduce_common_values(self, vehicle, date):
        self.ensure_one()
        return {
            'picking': self,
            'company': self.company_id,
            'vehicle': vehicle,
            'vehicle_type': self._get_vehicle_conduce_type(vehicle),
            'odometer_unit': {'kilometers': 'km', 'miles': 'mi'}.get(vehicle.odometer_unit, ''),
            'date_raw': date,
            'date': format_date(
                self.env, fields.Datetime.context_timestamp(self, date).date(),
                date_format='dd/MM/yyyy',
            ),
        }

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
        vehicle = self._get_vehicle_conduce_vehicle(moves, _('El Conduce de Salida'))
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
        return {
            **self._get_vehicle_conduce_common_values(vehicle, date),
            'title': 'CONDUCE DE SALIDA',
            'partner_label': 'Entregado a',
            'concept': 'ENTREGA DE VEHICULO',
            'legal_text': _(
                'Atención: Por medio de la presente, es para verificar correctamente la entrega del vehículo. '
                'Una vez recibido, se aceptan todas las condiciones indicadas en el presente documento y toda '
                'las responsabilidades por daños provocados a la unidad con posterioridad a su entrega. '
                'La aceptación de este documento conlleva a la conformidad con todo lo detallado en el mismo '
                'y lo hace responsable ante cualquier incidente o falla que pueda comprometer a FCR AUTOS S.R.L., '
                'o al titular de la matrícula hasta la ejecución del traspaso a su nombre. '
                'No firme en caso de diferencia.'
            ),
            'sale': sale,
            'partner': partner,
        }

    def _get_vehicle_conduce_incoming_values(self):
        """Validate receipt rules through purchase_stock relations, never origin text."""
        self.ensure_one()
        if self.picking_type_code != 'incoming':
            raise UserError(_(
                'El Conduce de Entrada solo corresponde a operaciones de entrada: %(picking)s.',
                picking=self.display_name,
            ))
        date = self._get_vehicle_conduce_date()
        moves = self._get_vehicle_conduce_moves()
        purchases = moves.purchase_line_id.order_id
        if not self.purchase_id or not purchases:
            raise UserError(_(
                'La transferencia %(picking)s no está vinculada a una compra mediante sus movimientos.',
                picking=self.display_name,
            ))
        if len(purchases) != 1 or purchases != self.purchase_id:
            raise UserError(_(
                'La transferencia %(picking)s tiene relaciones de compra ambiguas o contradictorias.',
                picking=self.display_name,
            ))
        purchase = purchases
        if purchase.company_id != self.company_id:
            raise UserError(_('La compra y la transferencia deben pertenecer a la misma compañía.'))
        vehicle = self._get_vehicle_conduce_vehicle(moves, _('El Conduce de Entrada'))
        vehicle_moves = moves.filtered(
            lambda move: move.product_id.product_tmpl_id.vehicle_id == vehicle
        )
        if any(
            move.purchase_line_id.order_id != purchase
            or move.purchase_line_id.product_id != move.product_id
            for move in vehicle_moves
        ):
            raise UserError(_(
                'Los movimientos del vehículo en %(picking)s deben estar vinculados '
                'a líneas del mismo producto en la compra correspondiente.',
                picking=self.display_name,
            ))
        partner = self.partner_id or purchase.partner_id
        if not partner:
            raise UserError(_('No se encontró el contacto proveedor de la recepción.'))
        return {
            **self._get_vehicle_conduce_common_values(vehicle, date),
            'title': 'CONDUCE DE ENTRADA',
            'partner_label': 'Recibido a',
            'concept': 'Adquisición FCR',
            'legal_text': _(
                'Acogiéndome a todas las estipulaciones contenidas en esta hoja de recepción, autorizo '
                'a FCR AUTOS S.R.L. a servir como agente de venta del bien dado en garantía prendaria y '
                'autorizo al potencial futuro comprador, a pagar directamente a FCR AUTOS S.R.L., la suma '
                'acordada entre ambas partes, más comisiones por servicios de venta, intereses sobre el '
                'avance de efectivo, gastos legales, gastos de almacenaje y cualquier otra suma resultante '
                'del presente acuerdo.'
            ),
            'purchase': purchase,
            'partner': partner,
        }

    def _get_or_create_vehicle_conduce(self, conduce_type):
        self.ensure_one()
        if conduce_type == 'outgoing':
            values = self._get_vehicle_conduce_outgoing_values()
        elif conduce_type == 'incoming':
            values = self._get_vehicle_conduce_incoming_values()
        else:
            raise UserError(_('Tipo de conduce no soportado: %(type)s.', type=conduce_type))

        Conduce = self.env['fcr.vehicle.conduce'].with_context(active_test=False)
        conduce = Conduce.search([
            ('picking_id', '=', self.id),
            ('conduce_type', '=', conduce_type),
        ], limit=1)
        if conduce:
            return conduce
        return Conduce.create({
            'picking_id': self.id,
            'conduce_type': conduce_type,
            'vehicle_id': values['vehicle'].id,
            'partner_id': values['partner'].id,
            'date': values['date_raw'],
        })

    def _action_open_vehicle_conduce(self, conduce_type):
        self.ensure_one()
        conduce = self._get_or_create_vehicle_conduce(conduce_type)
        action = self.env.ref('fcr_vehicle_conduce.action_vehicle_conduce').read()[0]
        action.update({
            'res_id': conduce.id,
            'views': [(self.env.ref('fcr_vehicle_conduce.view_vehicle_conduce_form').id, 'form')],
        })
        return action

    def action_open_vehicle_conduce_outgoing(self):
        return self._action_open_vehicle_conduce('outgoing')

    def action_open_vehicle_conduce_incoming(self):
        return self._action_open_vehicle_conduce('incoming')
