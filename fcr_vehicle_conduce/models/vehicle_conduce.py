from odoo import _, api, fields, models
from odoo.exceptions import UserError, ValidationError
from odoo.tools.misc import format_date


class FcrVehicleConduce(models.Model):
    _name = 'fcr.vehicle.conduce'
    _description = 'Conduce digital de vehículo'
    _order = 'date desc, id desc'

    CHECKLIST_FIELDS = (
        'check_lights',
        'check_gauges',
        'check_horns',
        'check_ac_vents',
        'check_rearview_mirrors',
        'check_glasses',
        'check_window_switches',
        'check_radio',
        'check_cassette_player',
        'check_cd_changer',
        'check_antenna',
        'check_air_conditioning',
        'check_cup_holder',
        'check_lighter',
        'check_center_console_lid',
        'check_ashtray',
        'check_headliner',
        'check_seat_upholstery',
        'check_moldings',
        'check_floor_mats',
        'check_door_lining',
        'check_oil_dipstick',
        'check_atf_dipstick',
        'check_engine_oil_cap',
        'check_hydraulic_oil_cap',
        'check_coolant_cap',
        'check_radiator_cap',
        'check_battery_no_7',
        'check_battery_terminal_cover',
        'check_engine_cover',
        'check_bumper_converter_cover',
        'check_lens',
        'check_wheel_center_cap',
        'check_spare_tire',
        'check_wheel_wrench',
        'check_jack',
        'check_keys',
        'check_pliers',
        'check_screwdriver',
    )

    # Coordinates are percentages over static/src/img/vehicle_inspection.png.
    CHECKLIST_MARK_COORDINATES = {
        'check_lights': (27.0, 14.2),
        'check_gauges': (27.0, 16.8),
        'check_horns': (27.0, 19.4),
        'check_ac_vents': (27.0, 22.0),
        'check_rearview_mirrors': (27.0, 24.6),
        'check_glasses': (27.0, 27.2),
        'check_window_switches': (27.0, 29.8),
        'check_radio': (27.0, 32.4),
        'check_cassette_player': (45.8, 14.2),
        'check_cd_changer': (45.8, 16.8),
        'check_antenna': (45.8, 19.4),
        'check_air_conditioning': (45.8, 22.0),
        'check_cup_holder': (45.8, 24.6),
        'check_lighter': (45.8, 27.2),
        'check_center_console_lid': (45.8, 29.8),
        'check_ashtray': (45.8, 32.4),
        'check_headliner': (67.1, 14.1),
        'check_seat_upholstery': (38.2, 60.9),
        'check_moldings': (38.2, 63.6),
        'check_floor_mats': (38.2, 66.3),
        'check_door_lining': (38.2, 69.0),
        'check_oil_dipstick': (15.2, 83.3),
        'check_atf_dipstick': (15.2, 86.0),
        'check_engine_oil_cap': (15.2, 88.7),
        'check_hydraulic_oil_cap': (15.2, 91.4),
        'check_coolant_cap': (31.4, 83.0),
        'check_radiator_cap': (31.4, 85.7),
        'check_battery_no_7': (31.4, 88.4),
        'check_battery_terminal_cover': (31.4, 91.1),
        'check_engine_cover': (31.4, 93.8),
        'check_bumper_converter_cover': (61.0, 82.0),
        'check_lens': (61.0, 84.7),
        'check_wheel_center_cap': (61.0, 87.4),
        'check_spare_tire': (61.0, 90.1),
        'check_wheel_wrench': (61.0, 92.8),
        'check_jack': (77.6, 82.1),
        'check_keys': (77.6, 84.8),
        'check_pliers': (77.6, 87.5),
        'check_screwdriver': (77.6, 90.2),
    }

    name = fields.Char(compute='_compute_name', store=True)
    document_title = fields.Char(compute='_compute_document_title')
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
    vehicle_model_year = fields.Selection(related='vehicle_id.model_year', string='Año')
    vehicle_license_plate = fields.Char(related='vehicle_id.license_plate', string='Placa')
    vehicle_vin_sn = fields.Char(related='vehicle_id.vin_sn', string='Chasis')
    vehicle_odometer = fields.Float(related='vehicle_id.odometer', string='Kms-Millas')
    vehicle_odometer_unit = fields.Selection(related='vehicle_id.odometer_unit', string='Unidad odómetro')
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
    inspector_signature = fields.Binary(string='Firma inspector', attachment=True, copy=False)
    inspector_signed_at = fields.Datetime(string='Fecha firma inspector', readonly=True, copy=False)
    client_signature = fields.Binary(string='Firma cliente', attachment=True, copy=False)
    client_signed_at = fields.Datetime(string='Fecha firma cliente', readonly=True, copy=False)
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

    snapshot_date = fields.Datetime(string='Snapshot fecha', readonly=True, copy=False)
    snapshot_title = fields.Char(string='Snapshot título', readonly=True, copy=False)
    snapshot_partner_label = fields.Char(string='Snapshot etiqueta contacto', readonly=True, copy=False)
    snapshot_partner_name = fields.Char(string='Snapshot contacto', readonly=True, copy=False)
    snapshot_partner_vat = fields.Char(string='Snapshot identificación', readonly=True, copy=False)
    snapshot_partner_phone = fields.Char(string='Snapshot teléfono', readonly=True, copy=False)
    snapshot_partner_email = fields.Char(string='Snapshot email', readonly=True, copy=False)
    snapshot_concept = fields.Char(string='Snapshot concepto', readonly=True, copy=False)
    snapshot_legal_text = fields.Text(string='Snapshot texto legal', readonly=True, copy=False)
    snapshot_vehicle_brand = fields.Char(string='Snapshot marca', readonly=True, copy=False)
    snapshot_vehicle_model = fields.Char(string='Snapshot modelo', readonly=True, copy=False)
    snapshot_vehicle_model_year = fields.Char(string='Snapshot año', readonly=True, copy=False)
    snapshot_vehicle_license_plate = fields.Char(string='Snapshot placa', readonly=True, copy=False)
    snapshot_vehicle_vin_sn = fields.Char(string='Snapshot chasis', readonly=True, copy=False)
    snapshot_vehicle_odometer = fields.Float(string='Snapshot odómetro', readonly=True, copy=False)
    snapshot_vehicle_odometer_unit = fields.Char(string='Snapshot unidad odómetro', readonly=True, copy=False)
    snapshot_vehicle_color = fields.Char(string='Snapshot color', readonly=True, copy=False)
    snapshot_vehicle_type = fields.Char(string='Snapshot tipo', readonly=True, copy=False)
    snapshot_inspector_id = fields.Many2one('res.users', string='Snapshot inspector', readonly=True, copy=False)
    snapshot_inspector_name = fields.Char(string='Snapshot nombre inspector', readonly=True, copy=False)
    snapshot_inspector_signature = fields.Binary(string='Snapshot firma inspector', attachment=True, readonly=True, copy=False)
    snapshot_inspector_signed_at = fields.Datetime(string='Snapshot fecha firma inspector', readonly=True, copy=False)
    snapshot_client_name = fields.Char(string='Snapshot nombre cliente', readonly=True, copy=False)
    snapshot_client_signature = fields.Binary(string='Snapshot firma cliente', attachment=True, readonly=True, copy=False)
    snapshot_client_signed_at = fields.Datetime(string='Snapshot fecha firma cliente', readonly=True, copy=False)
    snapshot_check_lights = fields.Boolean(string='Snapshot check_lights', readonly=True, copy=False)
    snapshot_check_gauges = fields.Boolean(string='Snapshot check_gauges', readonly=True, copy=False)
    snapshot_check_horns = fields.Boolean(string='Snapshot check_horns', readonly=True, copy=False)
    snapshot_check_ac_vents = fields.Boolean(string='Snapshot check_ac_vents', readonly=True, copy=False)
    snapshot_check_rearview_mirrors = fields.Boolean(string='Snapshot check_rearview_mirrors', readonly=True, copy=False)
    snapshot_check_glasses = fields.Boolean(string='Snapshot check_glasses', readonly=True, copy=False)
    snapshot_check_window_switches = fields.Boolean(string='Snapshot check_window_switches', readonly=True, copy=False)
    snapshot_check_radio = fields.Boolean(string='Snapshot check_radio', readonly=True, copy=False)
    snapshot_check_cassette_player = fields.Boolean(string='Snapshot check_cassette_player', readonly=True, copy=False)
    snapshot_check_cd_changer = fields.Boolean(string='Snapshot check_cd_changer', readonly=True, copy=False)
    snapshot_check_antenna = fields.Boolean(string='Snapshot check_antenna', readonly=True, copy=False)
    snapshot_check_air_conditioning = fields.Boolean(string='Snapshot check_air_conditioning', readonly=True, copy=False)
    snapshot_check_cup_holder = fields.Boolean(string='Snapshot check_cup_holder', readonly=True, copy=False)
    snapshot_check_lighter = fields.Boolean(string='Snapshot check_lighter', readonly=True, copy=False)
    snapshot_check_center_console_lid = fields.Boolean(string='Snapshot check_center_console_lid', readonly=True, copy=False)
    snapshot_check_ashtray = fields.Boolean(string='Snapshot check_ashtray', readonly=True, copy=False)
    snapshot_check_headliner = fields.Boolean(string='Snapshot check_headliner', readonly=True, copy=False)
    snapshot_check_seat_upholstery = fields.Boolean(string='Snapshot check_seat_upholstery', readonly=True, copy=False)
    snapshot_check_moldings = fields.Boolean(string='Snapshot check_moldings', readonly=True, copy=False)
    snapshot_check_floor_mats = fields.Boolean(string='Snapshot check_floor_mats', readonly=True, copy=False)
    snapshot_check_door_lining = fields.Boolean(string='Snapshot check_door_lining', readonly=True, copy=False)
    snapshot_check_oil_dipstick = fields.Boolean(string='Snapshot check_oil_dipstick', readonly=True, copy=False)
    snapshot_check_atf_dipstick = fields.Boolean(string='Snapshot check_atf_dipstick', readonly=True, copy=False)
    snapshot_check_engine_oil_cap = fields.Boolean(string='Snapshot check_engine_oil_cap', readonly=True, copy=False)
    snapshot_check_hydraulic_oil_cap = fields.Boolean(string='Snapshot check_hydraulic_oil_cap', readonly=True, copy=False)
    snapshot_check_coolant_cap = fields.Boolean(string='Snapshot check_coolant_cap', readonly=True, copy=False)
    snapshot_check_radiator_cap = fields.Boolean(string='Snapshot check_radiator_cap', readonly=True, copy=False)
    snapshot_check_battery_no_7 = fields.Boolean(string='Snapshot check_battery_no_7', readonly=True, copy=False)
    snapshot_check_battery_terminal_cover = fields.Boolean(string='Snapshot check_battery_terminal_cover', readonly=True, copy=False)
    snapshot_check_engine_cover = fields.Boolean(string='Snapshot check_engine_cover', readonly=True, copy=False)
    snapshot_check_bumper_converter_cover = fields.Boolean(string='Snapshot check_bumper_converter_cover', readonly=True, copy=False)
    snapshot_check_lens = fields.Boolean(string='Snapshot check_lens', readonly=True, copy=False)
    snapshot_check_wheel_center_cap = fields.Boolean(string='Snapshot check_wheel_center_cap', readonly=True, copy=False)
    snapshot_check_spare_tire = fields.Boolean(string='Snapshot check_spare_tire', readonly=True, copy=False)
    snapshot_check_wheel_wrench = fields.Boolean(string='Snapshot check_wheel_wrench', readonly=True, copy=False)
    snapshot_check_jack = fields.Boolean(string='Snapshot check_jack', readonly=True, copy=False)
    snapshot_check_keys = fields.Boolean(string='Snapshot check_keys', readonly=True, copy=False)
    snapshot_check_pliers = fields.Boolean(string='Snapshot check_pliers', readonly=True, copy=False)
    snapshot_check_screwdriver = fields.Boolean(string='Snapshot check_screwdriver', readonly=True, copy=False)


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

    @api.depends('conduce_type')
    def _compute_document_title(self):
        titles = {
            'incoming': _('CONDUCE DE ENTRADA'),
            'outgoing': _('CONDUCE DE SALIDA'),
        }
        for conduce in self:
            conduce.document_title = titles.get(conduce.conduce_type, _('CONDUCE DE VEHÍCULO'))

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
            if conduce.state == 'done':
                continue
            try:
                values = conduce._get_expected_conduce_values()
            except UserError as error:
                raise ValidationError(error.args[0]) from error
            if conduce.vehicle_id != values['vehicle'] or conduce.partner_id != values['partner']:
                raise ValidationError(_(
                    'El vehículo o contacto del conduce no coincide con la transferencia.'
                ))

    @api.constrains('state', 'inspector_signature', 'client_signature')
    def _check_done_signatures(self):
        for conduce in self:
            if conduce.state != 'done':
                continue
            signatures = conduce._get_signature_values()
            if not signatures['inspector_signature'] or not signatures['client_signature']:
                raise ValidationError(_('El conduce completado debe tener firma de inspector y cliente.'))

    @api.model
    def _get_checklist_fields(self):
        return self.CHECKLIST_FIELDS

    @api.model
    def _get_checklist_mark_coordinates(self):
        return self.CHECKLIST_MARK_COORDINATES

    @api.model
    def _validate_checklist_mark_mapping(self):
        fields_set = set(self.CHECKLIST_FIELDS)
        coordinates_set = set(self.CHECKLIST_MARK_COORDINATES)
        missing = fields_set - coordinates_set
        extra = coordinates_set - fields_set
        if missing or extra:
            raise UserError(_(
                'El mapeo visual del checklist no coincide con los campos: faltan %(missing)s; sobran %(extra)s.',
                missing=', '.join(sorted(missing)) or '-',
                extra=', '.join(sorted(extra)) or '-',
            ))
        return True

    def _get_expected_conduce_values(self):
        self.ensure_one()
        if self.conduce_type == 'incoming':
            return self.picking_id._get_vehicle_conduce_incoming_values()
        return self.picking_id._get_vehicle_conduce_outgoing_values()

    def _update_signature_metadata(self, vals):
        vals = dict(vals)
        now = fields.Datetime.now()
        if 'inspector_signature' in vals:
            vals['inspector_signed_at'] = now if vals.get('inspector_signature') else False
        if 'client_signature' in vals:
            vals['client_signed_at'] = now if vals.get('client_signature') else False
        return vals

    def write(self, vals):
        if vals and not self.env.context.get('vehicle_conduce_completion'):
            if any(conduce.state == 'done' for conduce in self):
                raise UserError(_('No puede modificar un conduce completado.'))
            if vals.get('state') == 'done':
                raise UserError(_('Use el botón Completar para completar el conduce.'))
            vals = self._update_signature_metadata(vals)
        return super().write(vals)

    @api.model_create_multi
    def create(self, vals_list):
        if not self.env.context.get('vehicle_conduce_completion'):
            new_vals_list = []
            for vals in vals_list:
                if vals.get('state') == 'done':
                    raise UserError(_('Use el botón Completar para completar el conduce.'))
                new_vals_list.append(self._update_signature_metadata(vals))
            vals_list = new_vals_list
        return super().create(vals_list)

    def _format_date(self, date):
        self.ensure_one()
        if not date:
            return ''
        return format_date(
            self.env,
            fields.Datetime.context_timestamp(self, date).date(),
            date_format='dd/MM/yyyy',
        )

    def _get_signature_values(self, values=None):
        self.ensure_one()
        values = values or self._get_expected_conduce_values()
        picking = self.picking_id
        partner = values['partner']
        inspector_name = picking.vehicle_conduce_inspector_name or self.inspector_id.name or self.env.user.name
        client_name = picking.vehicle_conduce_customer_name or partner.name
        return {
            'inspector_name': inspector_name,
            'inspector_signature': picking.vehicle_conduce_inspector_signature or self.inspector_signature,
            'client_name': client_name,
            'client_signature': picking.vehicle_conduce_customer_signature or self.client_signature,
        }

    def _snapshot_values(self, values, completion_date):
        self.ensure_one()
        partner = values['partner']
        vehicle = values['vehicle']
        signatures = self._get_signature_values(values)
        snapshot = {
            'snapshot_date': values['date_raw'],
            'snapshot_title': values['title'],
            'snapshot_partner_label': values['partner_label'],
            'snapshot_partner_name': partner.name,
            'snapshot_partner_vat': partner.vat,
            'snapshot_partner_phone': partner.phone,
            'snapshot_partner_email': partner.email,
            'snapshot_concept': values['concept'],
            'snapshot_legal_text': values['legal_text'],
            'snapshot_vehicle_brand': vehicle.brand_id.name,
            'snapshot_vehicle_model': vehicle.model_id.name,
            'snapshot_vehicle_model_year': vehicle.model_year,
            'snapshot_vehicle_license_plate': vehicle.license_plate,
            'snapshot_vehicle_vin_sn': vehicle.vin_sn,
            'snapshot_vehicle_odometer': vehicle.odometer,
            'snapshot_vehicle_odometer_unit': values['odometer_unit'],
            'snapshot_vehicle_color': vehicle.color,
            'snapshot_vehicle_type': values['vehicle_type'],
            'snapshot_inspector_id': self.inspector_id.id,
            'snapshot_inspector_name': signatures['inspector_name'],
            'snapshot_inspector_signature': signatures['inspector_signature'],
            'snapshot_inspector_signed_at': self.inspector_signed_at or completion_date,
            'snapshot_client_name': signatures['client_name'],
            'snapshot_client_signature': signatures['client_signature'],
            'snapshot_client_signed_at': self.client_signed_at or completion_date,
        }
        for field_name in self.CHECKLIST_FIELDS:
            snapshot[f'snapshot_{field_name}'] = self[field_name]
        return snapshot

    def action_mark_completed(self):
        self._validate_checklist_mark_mapping()
        for conduce in self:
            if conduce.state != 'draft':
                raise UserError(_('Solo puede completar conduces en borrador.'))
            values = conduce._get_expected_conduce_values()
            signatures = conduce._get_signature_values(values)
            if not signatures['inspector_signature']:
                raise UserError(_('Debe registrar la firma del inspector antes de completar el conduce.'))
            if not signatures['client_signature']:
                raise UserError(_('Debe registrar la firma del cliente antes de completar el conduce.'))
            if conduce.vehicle_id != values['vehicle'] or conduce.partner_id != values['partner']:
                raise UserError(_('El vehículo o contacto del conduce ya no coincide con la transferencia.'))
            completion_date = fields.Datetime.now()
            write_values = conduce._snapshot_values(values, completion_date)
            write_values.update({
                'inspector_signed_at': conduce.inspector_signed_at or completion_date,
                'client_signed_at': conduce.client_signed_at or completion_date,
                'state': 'done',
                'completed_by_id': self.env.user.id,
                'completed_date': completion_date,
            })
            if not write_values['snapshot_inspector_signed_at']:
                write_values['snapshot_inspector_signed_at'] = write_values['inspector_signed_at']
            if not write_values['snapshot_client_signed_at']:
                write_values['snapshot_client_signed_at'] = write_values['client_signed_at']
            conduce.with_context(vehicle_conduce_completion=True).write(write_values)
        return True

    def _check_value(self, field_name):
        self.ensure_one()
        if self.state == 'done':
            return self[f'snapshot_{field_name}']
        return self[field_name]

    def _get_active_check_marks(self):
        self.ensure_one()
        self._validate_checklist_mark_mapping()
        marks = []
        for field_name in self.CHECKLIST_FIELDS:
            if self._check_value(field_name):
                x, y = self.CHECKLIST_MARK_COORDINATES[field_name]
                marks.append({'field': field_name, 'x': x, 'y': y})
        return marks

    def _get_pdf_values(self):
        self.ensure_one()
        if self.state == 'done':
            return {
                'conduce_record': self,
                'picking': self.picking_id,
                'company': self.company_id,
                'title': self.snapshot_title,
                'partner_label': self.snapshot_partner_label,
                'partner_name': self.snapshot_partner_name,
                'partner_vat': self.snapshot_partner_vat,
                'partner_phone': self.snapshot_partner_phone,
                'partner_email': self.snapshot_partner_email,
                'concept': self.snapshot_concept,
                'legal_text': self.snapshot_legal_text,
                'vehicle_brand': self.snapshot_vehicle_brand,
                'vehicle_model': self.snapshot_vehicle_model,
                'vehicle_model_year': self.snapshot_vehicle_model_year,
                'vehicle_license_plate': self.snapshot_vehicle_license_plate,
                'vehicle_vin_sn': self.snapshot_vehicle_vin_sn,
                'vehicle_odometer': self.snapshot_vehicle_odometer,
                'odometer_unit': self.snapshot_vehicle_odometer_unit,
                'vehicle_color': self.snapshot_vehicle_color,
                'vehicle_type': self.snapshot_vehicle_type,
                'date_raw': self.snapshot_date,
                'date': self._format_date(self.snapshot_date),
                'inspector_name': self.snapshot_inspector_name,
                'inspector_signature': self.snapshot_inspector_signature,
                'client_name': self.snapshot_client_name or self.snapshot_partner_name,
                'client_signature': self.snapshot_client_signature,
                'check_marks': self._get_active_check_marks(),
                'state': self.state,
            }
        values = self._get_expected_conduce_values()
        partner = values['partner']
        vehicle = values['vehicle']
        signatures = self._get_signature_values(values)
        return {
            **values,
            'conduce_record': self,
            'partner_name': partner.name,
            'partner_vat': partner.vat,
            'partner_phone': partner.phone,
            'partner_email': partner.email,
            'vehicle_brand': vehicle.brand_id.name,
            'vehicle_model': vehicle.model_id.name,
            'vehicle_model_year': vehicle.model_year,
            'vehicle_license_plate': vehicle.license_plate,
            'vehicle_vin_sn': vehicle.vin_sn,
            'vehicle_odometer': vehicle.odometer,
            'vehicle_color': vehicle.color,
            'inspector_name': signatures['inspector_name'],
            'inspector_signature': signatures['inspector_signature'],
            'client_name': signatures['client_name'],
            'client_signature': signatures['client_signature'],
            'check_marks': self._get_active_check_marks(),
            'state': self.state,
        }
