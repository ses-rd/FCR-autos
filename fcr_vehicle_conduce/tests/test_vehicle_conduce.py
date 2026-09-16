from datetime import datetime
from uuid import uuid4

from lxml import html as html_parser

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
        cls.warehouse = cls.env['stock.warehouse'].create({
            'name': 'Conduce test warehouse', 'code': uuid4().hex[:5],
            'company_id': cls.env.company.id,
        })
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

    def test_assigned_date_timezone_and_missing_date(self):
        picking, _sale = self._picking()
        picking.scheduled_date = datetime(2026, 6, 29, 1, 0)
        self.assertEqual(
            picking.with_context(tz='America/Santo_Domingo')._get_vehicle_conduce_outgoing_values()['date'],
            '28/06/2026',
        )
        # Test the date rule on an in-memory record: the stored scheduling field
        # has an inverse which may prevent clearing it through the normal UI.
        empty_date = self.env['stock.picking'].new({'state': 'assigned', 'scheduled_date': False})
        with self.assertRaisesRegex(UserError, 'fecha efectiva'):
            empty_date._get_vehicle_conduce_date()

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

    def test_stale_backlinks_do_not_override_moved_product(self):
        picking, _sale = self._picking()
        vehicle = picking.move_ids.product_id.product_tmpl_id.vehicle_id
        other_product, _vehicle = self._vehicle_product()
        vehicle.write({
            'product_id': other_product.id,
            'product_tmpl_id': other_product.product_tmpl_id.id,
        })
        self.assertEqual(picking._get_vehicle_conduce_outgoing_values()['vehicle'], vehicle)
        vehicle.write({'product_id': False, 'product_tmpl_id': False})
        self.assertEqual(picking._get_vehicle_conduce_outgoing_values()['vehicle'], vehicle)

    def test_multiple_products_resolving_same_vehicle(self):
        picking, sale = self._picking()
        vehicle = picking.move_ids.product_id.product_tmpl_id.vehicle_id
        product = self.env['product.product'].create({
            'name': 'Historical vehicle product', 'type': 'consu', 'vehicle_id': vehicle.id,
        })
        line = self.env['sale.order.line'].create({'order_id': sale.id, 'product_id': product.id})
        self._move(picking, product, line)
        self.assertEqual(picking._get_vehicle_conduce_outgoing_values()['vehicle'], vehicle)

    def test_archived_vehicle_and_unset_is_fleet(self):
        picking, _sale = self._picking()
        product = picking.move_ids.product_id
        vehicle = product.product_tmpl_id.vehicle_id
        product.is_fleet = False
        vehicle.active = False
        self.assertEqual(picking._get_vehicle_conduce_outgoing_values()['vehicle'], vehicle)

    def test_accessory_does_not_count_as_vehicle(self):
        picking, _sale = self._picking()
        vehicle = picking.move_ids.product_id.product_tmpl_id.vehicle_id
        accessory = self.env['product.product'].create({'name': 'Accessory', 'type': 'consu'})
        self._move(picking, accessory)
        self.assertEqual(picking._get_vehicle_conduce_outgoing_values()['vehicle'], vehicle)
        accessory.is_fleet = True
        with self.assertRaisesRegex(UserError, 'sin vínculo'):
            picking._get_vehicle_conduce_outgoing_values()

    def test_sale_line_product_mismatch_rejected(self):
        picking, _sale = self._picking()
        other_product, _vehicle = self._vehicle_product()
        picking.move_ids.sale_line_id.product_id = other_product
        with self.assertRaises(UserError):
            picking._get_vehicle_conduce_outgoing_values()

    def test_foreign_vehicle_company_rejected(self):
        picking, _sale = self._picking()
        company = self.env['res.company'].create({'name': 'Other conduce test company'})
        picking.move_ids.product_id.product_tmpl_id.vehicle_id.company_id = company
        with self.assertRaisesRegex(UserError, 'otra compañía'):
            picking._get_vehicle_conduce_outgoing_values()

    def test_type_fallback_and_shared_vehicle(self):
        picking, _sale = self._picking()
        vehicle = picking.move_ids.product_id.product_tmpl_id.vehicle_id
        vehicle.write({'category_id': False, 'company_id': False})
        expected = dict(vehicle._fields['vehicle_type']._description_selection(self.env))[vehicle.vehicle_type]
        self.assertEqual(picking._get_vehicle_conduce_outgoing_values()['vehicle_type'], expected)

    def test_empty_contact_fields_are_not_filled_from_parent(self):
        picking, _sale = self._picking()
        self.customer.write({'phone': '809-555-0199', 'email': 'parent@example.test'})
        self.recipient.write({'phone': False, 'email': False, 'vat': False})
        html, _kind = self.env['ir.actions.report']._render_qweb_html(self.report.report_name, picking.ids)
        text = html_parser.fromstring(html).text_content()
        self.assertIn(self.recipient.name, text)
        self.assertNotIn('809-555-0199', text)
        self.assertNotIn('parent@example.test', text)

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
        with self.assertRaises(UserError):
            self.report_model._get_report_values(None)
        documents = self.report_model._get_report_values([valid.id, valid.id])
        self.assertEqual(len(documents['conduce_documents']), 1)

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

    def test_render_escapes_dynamic_html_and_preserves_long_values(self):
        picking, _sale = self._picking()
        self.recipient.name = '<script>alert("test")</script> Cliente & Asociados ' + 'Nombre largo ' * 6
        vehicle = picking.move_ids.product_id.product_tmpl_id.vehicle_id
        vehicle.vin_sn = 'VIN' + '1234567890' * 5
        html, _kind = self.env['ir.actions.report']._render_qweb_html(self.report.report_name, picking.ids)
        document = html_parser.fromstring(html)
        content = document.xpath('//div[contains(@class, "fcr-content")]')[0]
        self.assertFalse(content.xpath('.//script'))
        self.assertIn(self.recipient.name, content.text_content())
        self.assertIn(vehicle.vin_sn, content.text_content())

    def test_batch_html_and_printing_does_not_change_inventory(self):
        first, _sale = self._picking()
        second, _sale = self._picking()
        pickings = first | second
        before_pickings = pickings.read(['state', 'scheduled_date', 'date_done'])
        before_moves = pickings.move_ids.read(['state', 'quantity', 'product_uom_qty'])
        quant_domain = [('product_id', 'in', pickings.move_ids.product_id.ids)]
        before_quants = self.env['stock.quant'].search(quant_domain).read(['quantity', 'reserved_quantity'])
        html, _kind = self.env['ir.actions.report']._render_qweb_html(self.report.report_name, pickings.ids)
        document = html_parser.fromstring(html)
        self.assertEqual(len(document.xpath('//div[contains(@class, "fcr-conduce-article")]')), 2)
        self.assertEqual(pickings.read(['state', 'scheduled_date', 'date_done']), before_pickings)
        self.assertEqual(pickings.move_ids.read(['state', 'quantity', 'product_uom_qty']), before_moves)
        self.assertEqual(self.env['stock.quant'].search(quant_domain).read(['quantity', 'reserved_quantity']), before_quants)
