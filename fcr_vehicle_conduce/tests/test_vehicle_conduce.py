from datetime import datetime

from odoo.exceptions import UserError
from odoo.tests import TransactionCase, tagged


@tagged('post_install', '-at_install')
class TestVehicleConduce(TransactionCase):
    """Run on a disposable Odoo database, never against operational records."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.customer = cls.env['res.partner'].create({'name': 'Conduce test customer'})
        cls.recipient = cls.env['res.partner'].create({
            'name': 'Conduce test recipient', 'parent_id': cls.customer.id, 'type': 'delivery',
            'phone': '809-555-0100', 'email': 'recipient@example.test',
        })
        cls.warehouse = cls.env['stock.warehouse'].search([
            ('company_id', '=', cls.env.company.id),
        ], limit=1)
        cls.brand = cls.env['fleet.vehicle.model.brand'].create({'name': 'Test brand'})
        cls.vehicle_model = cls.env['fleet.vehicle.model'].create({
            'name': 'Test model', 'brand_id': cls.brand.id,
        })
        cls.category = cls.env['fleet.vehicle.model.category'].create({'name': 'Camioneta'})
        cls.report = cls.env.ref('fcr_vehicle_conduce.action_report_vehicle_conduce_outgoing')
        cls.report_model = cls.env['report.fcr_vehicle_conduce.report_vehicle_conduce_outgoing']

    def _vehicle_product(self):
        vehicle = self.env['fleet.vehicle'].create({
            'model_id': self.vehicle_model.id, 'company_id': self.env.company.id,
            'license_plate': 'TEST-PLATE', 'vin_sn': 'TEST-CHASSIS',
            'category_id': self.category.id,
        })
        product = self.env['product.product'].create({
            'name': 'Test vehicle', 'type': 'consu', 'is_storable': True,
            'is_fleet': True, 'vehicle_id': vehicle.id,
        })
        vehicle.write({'product_id': product.id, 'product_tmpl_id': product.product_tmpl_id.id})
        return product, vehicle

    def _picking(self, product=None, linked=True, picking_type=None):
        product = product or self._vehicle_product()[0]
        sale = self.env['sale.order'].create({
            'partner_id': self.customer.id, 'partner_shipping_id': self.recipient.id,
        })
        line = self.env['sale.order.line'].create({
            'order_id': sale.id, 'product_id': product.id, 'product_uom_qty': 1,
        })
        picking_type = picking_type or self.warehouse.out_type_id
        picking = self.env['stock.picking'].create({
            'picking_type_id': picking_type.id, 'partner_id': self.recipient.id,
            'location_id': self.warehouse.lot_stock_id.id,
            'location_dest_id': self.env.ref('stock.stock_location_customers').id,
        })
        self._move(picking, product, line if linked else False)
        picking.scheduled_date = datetime(2026, 6, 28, 16, 0)
        return picking, sale

    def _move(self, picking, product, line=False, state='assigned', demand=1):
        return self.env['stock.move'].create({
            'product_id': product.id,
            'product_uom': product.uom_id.id, 'product_uom_qty': demand,
            'picking_id': picking.id, 'location_id': picking.location_id.id,
            'location_dest_id': picking.location_dest_id.id,
            'sale_line_id': line.id if line else False, 'state': state,
        })

    def test_ready_delivery_contact_vehicle_and_scheduled_date(self):
        product, vehicle = self._vehicle_product()
        picking, sale = self._picking(product)
        values = picking.with_context(tz='America/Santo_Domingo')._get_vehicle_conduce_outgoing_values()
        self.assertEqual(values['sale'], sale)
        self.assertEqual(values['partner'], self.recipient)
        self.assertEqual(values['vehicle'], vehicle)
        self.assertEqual(values['date'], '28/06/2026')
        self.assertEqual(values['vehicle_type'], 'Camioneta')

    def test_contact_fallbacks(self):
        picking, sale = self._picking()
        picking.partner_id = False
        self.assertEqual(picking._get_vehicle_conduce_outgoing_values()['partner'], sale.partner_shipping_id)

    def test_origin_does_not_establish_sale(self):
        picking, sale = self._picking(linked=False)
        picking.origin = sale.name
        with self.assertRaisesRegex(UserError, 'venta'):
            picking._get_vehicle_conduce_outgoing_values()

    def test_incoming_rejected(self):
        picking, _sale = self._picking(picking_type=self.warehouse.in_type_id)
        with self.assertRaisesRegex(UserError, 'operaciones de salida'):
            picking._get_vehicle_conduce_outgoing_values()

    def test_not_ready_rejected(self):
        picking, _sale = self._picking()
        picking.move_ids.state = 'confirmed'
        with self.assertRaisesRegex(UserError, 'Lista o Hecha'):
            picking._get_vehicle_conduce_outgoing_values()

    def test_missing_vehicle_rejected(self):
        product = self.env['product.product'].create({'name': 'No Fleet link', 'type': 'consu'})
        picking, _sale = self._picking(product)
        with self.assertRaisesRegex(UserError, 'No hay un vehículo'):
            picking._get_vehicle_conduce_outgoing_values()
        product.is_fleet = True
        with self.assertRaisesRegex(UserError, 'sin vínculo'):
            picking._get_vehicle_conduce_outgoing_values()

    def test_multiple_vehicles_rejected(self):
        picking, sale = self._picking()
        product, _vehicle = self._vehicle_product()
        line = self.env['sale.order.line'].create({'order_id': sale.id, 'product_id': product.id})
        self._move(picking, product, line)
        with self.assertRaisesRegex(UserError, 'varios vehículos'):
            picking._get_vehicle_conduce_outgoing_values()

    def test_cancelled_zero_and_other_order_products_ignored(self):
        picking, sale = self._picking()
        expected = picking.move_ids.product_id.product_tmpl_id.vehicle_id
        product, _vehicle = self._vehicle_product()
        line = self.env['sale.order.line'].create({'order_id': sale.id, 'product_id': product.id})
        self._move(picking, product, line, state='cancel')
        self._move(picking, product, line, demand=0)
        self.assertEqual(picking._get_vehicle_conduce_outgoing_values()['vehicle'], expected)

    def test_multiple_sales_rejected(self):
        picking, _sale = self._picking()
        other, _other_sale = self._picking()
        self._move(picking, other.move_ids.product_id, other.move_ids.sale_line_id)
        with self.assertRaisesRegex(UserError, 'relaciones de venta'):
            picking._get_vehicle_conduce_outgoing_values()

    def test_vehicle_requires_its_own_sale_line(self):
        picking, sale = self._picking()
        picking.move_ids.sale_line_id = False
        accessory = self.env['product.product'].create({'name': 'Accessory', 'type': 'consu'})
        line = self.env['sale.order.line'].create({'order_id': sale.id, 'product_id': accessory.id})
        self._move(picking, accessory, line)
        with self.assertRaisesRegex(UserError, 'movimientos del vehículo'):
            picking._get_vehicle_conduce_outgoing_values()

    def test_inconsistent_backlink_rejected(self):
        picking, _sale = self._picking()
        other_product, _vehicle = self._vehicle_product()
        picking.move_ids.product_id.product_tmpl_id.vehicle_id.product_id = other_product
        with self.assertRaisesRegex(UserError, 'contradictorio'):
            picking._get_vehicle_conduce_outgoing_values()

    def test_done_date_and_timezone(self):
        picking, _sale = self._picking()
        picking.move_ids.write({'quantity': 1, 'state': 'done'})
        picking.date_done = datetime(2026, 7, 2, 1, 0)
        values = picking.with_context(tz='America/Santo_Domingo')._get_vehicle_conduce_outgoing_values()
        self.assertEqual(values['date'], '01/07/2026')
        picking.date_done = False
        with self.assertRaisesRegex(UserError, 'fecha efectiva'):
            picking._get_vehicle_conduce_outgoing_values()

    def test_report_rejects_mixed_batch_and_missing_ids(self):
        valid, _sale = self._picking()
        invalid, _sale = self._picking(linked=False)
        with self.assertRaises(UserError):
            self.report_model._get_report_values((valid | invalid).ids)
        with self.assertRaises(UserError):
            self.report_model._get_report_values([])
        with self.assertRaises(UserError):
            self.report_model._get_report_values([0])

    def test_print_domain_and_letter_format(self):
        picking, _sale = self._picking()
        self.assertIn(self.report.id, self.report.get_valid_action_reports('stock.picking', picking.ids))
        picking.move_ids.state = 'cancel'
        self.assertNotIn(self.report.id, self.report.get_valid_action_reports('stock.picking', picking.ids))
        self.assertEqual(self.report.paperformat_id.format, 'Letter')
        self.assertAlmostEqual(self.report.paperformat_id.print_page_width, 215.9)
        self.assertAlmostEqual(self.report.paperformat_id.print_page_height, 279.4)

    def test_qweb_html_contains_vehicle_and_static_checklist(self):
        picking, _sale = self._picking()
        html, _kind = self.env['ir.actions.report']._render_qweb_html(self.report.report_name, picking.ids)
        html = html.decode()
        for text in ('CONDUCE DE SALIDA', 'TEST-CHASSIS', 'Conduce test recipient',
                     'vehicle_inspection.png', 'Inspector', 'Cliente', 'No firme en caso de diferencia.'):
            self.assertIn(text, html)
