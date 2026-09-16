from odoo import _, api, fields, models
from odoo.exceptions import UserError, ValidationError


class FcrVehicleConduce(models.Model):
    _name = 'fcr.vehicle.conduce'
    _description = 'Conduce digital de vehículo'
    _order = 'date desc, id desc'

    name = fields.Char(compute='_compute_name', store=True)
    active = fields.Boolean(default=True)
    picking_id = fields.Many2one('stock.picking', required=True, readonly=True, ondelete='restrict', index=True)
    company_id = fields.Many2one(related='picking_id.company_id', store=True, readonly=True)
    conduce_type = fields.Selection(
        [('incoming', 'Entrada'), ('outgoing', 'Salida')],
        string='Tipo',
        required=True,
        readonly=True,
        index=True,
    )
    state = fields.Selection(
        [('draft', 'Borrador'), ('done', 'Completado')],
        default='draft',
        required=True,
        index=True,
    )
    vehicle_id = fields.Many2one('fleet.vehicle', required=True, readonly=True)
    vehicle_brand_id = fields.Many2one(related='vehicle_id.brand_id', string='Marca')
    vehicle_model_id = fields.Many2one(related='vehicle_id.model_id', string='Modelo')
    vehicle_model_year = fields.Char(related='vehicle_id.model_year', string='Año')
    vehicle_license_plate = fields.Char(related='vehicle_id.license_plate', string='Placa')
    vehicle_vin_sn = fields.Char(related='vehicle_id.vin_sn', string='Chasis')
    vehicle_odometer = fields.Float(related='vehicle_id.odometer', string='Kms-Millas')
    vehicle_color = fields.Char(related='vehicle_id.color', string='Color')
    vehicle_category_id = fields.Many2one(related='vehicle_id.category_id', string='Tipo')
    partner_id = fields.Many2one('res.partner', string='Contacto', required=True, readonly=True)
    date = fields.Datetime(required=True, readonly=True)
    inspector_id = fields.Many2one(
        'res.users',
        string='Inspector',
        default=lambda self: self.env.user,
        required=True,
        readonly=True,
    )
    completed_by_id = fields.Many2one('res.users', string='Completado por', readonly=True, copy=False)
    completed_date = fields.Datetime(string='Fecha de completado', readonly=True, copy=False)

    check_lights = fields.Boolean(string='Luces')
    check_gauges = fields.Boolean(string='Relojes')
    check_horns = fields.Boolean(string='Bocinas')
    check_ac_vents = fields.Boolean(string='Rejillas A/C')
    check_rearview_mirrors = fields.Boolean(string='Espejos Retrovisor')
    check_glasses = fields.Boolean(string='Cristales')
    check_window_switches = fields.Boolean(string='Switch Cristales')
    check_radio = fields.Boolean(string='Radio')
    check_cassette_player = fields.Boolean(string='Toca Cassette')
    check_cd_changer = fields.Boolean(string='CD Changer')
    check_antenna = fields.Boolean(string='Antena')
    check_air_conditioning = fields.Boolean(string='Aire Acondicionado')
    check_cup_holder = fields.Boolean(string='Porta Vasos')
    check_lighter = fields.Boolean(string='Encendedor')
    check_center_console_lid = fields.Boolean(string='Tapa Consola Central')
    check_ashtray = fields.Boolean(string='Gaveta Cenicero')
    check_headliner = fields.Boolean(string='Forro Techo')
    check_seat_upholstery = fields.Boolean(string='Tapizados Asientos')
    check_moldings = fields.Boolean(string='Molduras')
    check_floor_mats = fields.Boolean(string='Alfombras')
    check_door_lining = fields.Boolean(string='Forro Puertas')

    check_oil_dipstick = fields.Boolean(string='Varilla de Aceite')
    check_atf_dipstick = fields.Boolean(string='Varilla ATF')
    check_engine_oil_cap = fields.Boolean(string='Tapón Aceite Motor')
    check_hydraulic_oil_cap = fields.Boolean(string='Tapón Aceite Hidráulico')
    check_coolant_cap = fields.Boolean(string='Tapón de Coolant')
    check_radiator_cap = fields.Boolean(string='Tapón de Radiador')
    check_battery_no_7 = fields.Boolean(string='Baterías No. 7')
    check_battery_terminal_cover = fields.Boolean(string='Cover Polo Batería')
    check_engine_cover = fields.Boolean(string='Cover Tapa de Motor')
    check_bumper_converter_cover = fields.Boolean(string='Tapa Convertora Bumper')
    check_lens = fields.Boolean(string='Mica')
    check_wheel_center_cap = fields.Boolean(string='Tapa Bocina/Centro Aro')
    check_spare_tire = fields.Boolean(string='Goma de Repuesto')
    check_wheel_wrench = fields.Boolean(string='Llave Ruedas')
    check_jack = fields.Boolean(string='Gato')
    check_keys = fields.Boolean(string='Llaves')
    check_pliers = fields.Boolean(string='Alicate')
    check_screwdriver = fields.Boolean(string='Destornillador')

    _sql_constraints = [
        (
            'unique_picking_conduce_type',
            'unique(picking_id, conduce_type)',
            'Ya existe un conduce de este tipo para esta transferencia.',
        ),
    ]

    @api.depends('conduce_type', 'picking_id.name')
    def _compute_name(self):
        labels = dict(self._fields['conduce_type'].selection)
        for conduce in self:
            if conduce.picking_id and conduce.conduce_type:
                conduce.name = _('Conduce de %(type)s - %(picking)s',
                                 type=labels[conduce.conduce_type],
                                 picking=conduce.picking_id.name)
            else:
                conduce.name = _('Conduce de vehículo')

    @api.constrains('picking_id', 'conduce_type')
    def _check_picking_type_matches_conduce_type(self):
        expected = {'incoming': 'incoming', 'outgoing': 'outgoing'}
        for conduce in self:
            if conduce.picking_id.picking_type_code != expected.get(conduce.conduce_type):
                raise ValidationError(_(
                    'El tipo del conduce no coincide con el tipo de operación de la transferencia.'
                ))

    @api.constrains('picking_id', 'conduce_type', 'vehicle_id', 'partner_id')
    def _check_resolved_vehicle_and_partner(self):
        for conduce in self:
            try:
                if conduce.conduce_type == 'incoming':
                    values = conduce.picking_id._get_vehicle_conduce_incoming_values()
                else:
                    values = conduce.picking_id._get_vehicle_conduce_outgoing_values()
            except UserError as error:
                raise ValidationError(error.args[0]) from error
            if conduce.vehicle_id != values['vehicle'] or conduce.partner_id != values['partner']:
                raise ValidationError(_(
                    'El vehículo o contacto del conduce no coincide con la transferencia.'
                ))

    def action_mark_completed(self):
        for conduce in self:
            conduce.write({
                'state': 'done',
                'completed_by_id': self.env.user.id,
                'completed_date': fields.Datetime.now(),
            })
        return True
