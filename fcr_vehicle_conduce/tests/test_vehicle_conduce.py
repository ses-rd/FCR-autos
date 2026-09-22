from base64 import b64encode
from datetime import datetime
from uuid import uuid4

from lxml import html as html_parser

from odoo.exceptions import UserError
from odoo.tests import TransactionCase, tagged
from odoo.tools.safe_eval import safe_eval


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
        cls.incoming_report = cls.env.ref('fcr_vehicle_conduce.action_report_vehicle_conduce_incoming')
        cls.incoming_report_model = cls.env['report.fcr_vehicle_conduce.report_vehicle_conduce_incoming']

    def _signature(self, label='signature'):
        return b64encode(label.encode())

    def _sign_conduce(self, conduce):
        conduce.write({
            'inspector_signature': self._signature('inspector'),
            'client_signature': self._signature('client'),
        })

    def _sign_picking(self, picking, inspector='Inspector Tablet', customer='Cliente Tablet'):
        picking.write({
            'vehicle_conduce_inspector_name': inspector,
            'vehicle_conduce_inspector_signature': self._signature('picking inspector'),
            'vehicle_conduce_customer_name': customer,
            'vehicle_conduce_customer_signature': self._signature('picking customer'),
        })

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

    def _purchase_picking(self, products=None, vendor=None):
        products = products or [self._vehicle_product()[0]]
        vendor = vendor or self.env['res.partner'].create({
            'name': 'Conduce test vendor',
            'phone': '809-555-0200',
            'email': 'vendor@example.test',
            'vat': '101010101',
        })
        purchase = self.env['purchase.order'].create({
            'partner_id': vendor.id,
            'picking_type_id': self.warehouse.in_type_id.id,
            'company_id': self.env.company.id,
        })
        for product in products:
            self.env['purchase.order.line'].create({
                'order_id': purchase.id,
                'product_id': product.id,
                'product_qty': 1,
                'product_uom_id': product.uom_id.id,
                'price_unit': 1,
                'date_planned': datetime(2026, 6, 28, 16, 0),
            })
        purchase.button_confirm()
        picking = purchase.picking_ids.filtered(lambda p: p.picking_type_code == 'incoming')[:1]
        picking.scheduled_date = datetime(2026, 6, 28, 16, 0)
        picking.move_ids.state = 'assigned'
        return picking, purchase, vendor

    def _manual_incoming_picking(self, products=None, partner=None, entry_type='consignment'):
        products = products or [self._vehicle_product()[0]]
        if partner is None:
            partner = self.env['res.partner'].create({
                'name': 'Conduce test consignor',
                'phone': '809-555-0300',
                'email': 'consignor@example.test',
                'vat': '202020202',
            })
        picking = self.env['stock.picking'].create({
            'picking_type_id': self.warehouse.in_type_id.id,
            'partner_id': partner.id if partner else False,
            'location_id': self.env.ref('stock.stock_location_suppliers').id,
            'location_dest_id': self.warehouse.lot_stock_id.id,
            'vehicle_entry_type': entry_type,
        })
        for product in products:
            self._move(picking, product)
        picking.scheduled_date = datetime(2026, 6, 28, 16, 0)
        picking.move_ids.state = 'assigned'
        return picking, partner

    def test_ready_delivery_contact_vehicle_and_scheduled_date(self):
        product, vehicle = self._vehicle_product()
        picking, sale = self._picking(product)
        values = picking.with_context(tz='America/Santo_Domingo')._get_vehicle_conduce_outgoing_values()
        self.assertEqual(values['sale'], sale)
        self.assertEqual(values['partner'], self.recipient)
        self.assertEqual(values['vehicle'], vehicle)
        self.assertEqual(values['date'], '28/06/2026')
        self.assertEqual(values['vehicle_type'], 'Camioneta')

    def test_vehicle_resolution_accepts_direct_and_inverse_product_links(self):
        product, vehicle = self._vehicle_product()
        picking, _sale = self._picking(product)
        self.assertEqual(picking._get_vehicle_conduce_outgoing_values()['vehicle'], vehicle)

        product.product_tmpl_id.vehicle_id = False
        self.assertEqual(picking._get_vehicle_conduce_outgoing_values()['vehicle'], vehicle)

        vehicle.product_id = False
        self.assertEqual(picking._get_vehicle_conduce_outgoing_values()['vehicle'], vehicle)

    def test_vehicle_resolution_accepts_inverse_product_variant_link(self):
        product, vehicle = self._vehicle_product()
        product.product_tmpl_id.vehicle_id = False
        vehicle.product_tmpl_id = False
        picking, _sale = self._picking(product)
        values = picking._get_vehicle_conduce_outgoing_values()
        self.assertEqual(values['vehicle'], vehicle)
        report_values = self.report_model._get_report_values([picking.id])
        self.assertEqual(report_values['conduce_documents'][0]['vehicle'], vehicle)
        conduce = self.env['fcr.vehicle.conduce'].browse(
            picking.action_open_vehicle_conduce_outgoing()['res_id']
        )
        self.assertEqual(conduce.vehicle_id, vehicle)

    def test_vehicle_resolution_accepts_inverse_template_link(self):
        product, vehicle = self._vehicle_product()
        product.product_tmpl_id.vehicle_id = False
        vehicle.product_id = False
        picking, _sale = self._picking(product)
        values = picking._get_vehicle_conduce_outgoing_values()
        self.assertEqual(values['vehicle'], vehicle)
        conduce = self.env['fcr.vehicle.conduce'].browse(
            picking.action_open_vehicle_conduce_outgoing()['res_id']
        )
        self.assertEqual(conduce.vehicle_id, vehicle)

    def test_conflicting_explicit_vehicle_links_are_rejected(self):
        product, _vehicle = self._vehicle_product()
        other_vehicle = self.env['fleet.vehicle'].create({
            'model_id': self.vehicle_model.id,
            'company_id': self.env.company.id,
            'license_plate': 'CONFLICT-PLATE',
        })
        other_vehicle.product_id = product
        picking, _sale = self._picking(product)
        with self.assertRaisesRegex(UserError, 'varios veh'):
            picking._get_vehicle_conduce_outgoing_values()

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

    def _stock_reference_for_sale(self, sale):
        return self.env['stock.reference'].create({
            'name': sale.name,
            'sale_ids': [(4, sale.id)],
        })

    def test_sale_resolution_accepts_move_sale_line(self):
        picking, sale = self._picking()
        self.assertEqual(picking._get_vehicle_conduce_sale(picking._get_vehicle_conduce_moves()), sale)
        self.assertEqual(picking._get_vehicle_conduce_outgoing_values()['sale'], sale)

    def test_outgoing_conduce_works_without_sale_or_incoming_conduce(self):
        picking, _sale = self._picking(linked=False)
        self.assertFalse(picking._get_vehicle_conduce_sale(picking._get_vehicle_conduce_moves()))
        values = picking._get_vehicle_conduce_outgoing_values()
        self.assertFalse(values['sale'])
        self.assertEqual(values['partner'], self.recipient)
        self.assertEqual(values['vehicle'], picking.move_ids.product_id.product_tmpl_id.vehicle_id)
        self.assertFalse(self.env['fcr.vehicle.conduce'].search([
            ('vehicle_id', '=', values['vehicle'].id),
            ('conduce_type', '=', 'incoming'),
        ]))
        report_values = self.report_model._get_report_values([picking.id])
        self.assertFalse(report_values['conduce_documents'][0]['sale'])
        conduce = self.env['fcr.vehicle.conduce'].browse(
            picking.action_open_vehicle_conduce_outgoing()['res_id']
        )
        self.assertEqual(conduce.vehicle_id, values['vehicle'])
        self.assertEqual(conduce.partner_id, self.recipient)

    def test_sale_resolution_accepts_stock_reference_without_sale_line(self):
        picking, sale = self._picking(linked=False)
        reference = self._stock_reference_for_sale(sale)
        picking.move_ids.reference_ids = [(4, reference.id)]
        self.assertEqual(picking._get_vehicle_conduce_sale(picking._get_vehicle_conduce_moves()), sale)
        values = picking._get_vehicle_conduce_outgoing_values()
        self.assertEqual(values['sale'], sale)
        self.assertEqual(values['partner'], self.recipient)
        self.assertEqual(values['vehicle'], picking.move_ids.product_id.product_tmpl_id.vehicle_id)
        before_sale = sale.read(['partner_id', 'partner_shipping_id', 'state', 'amount_total'])[0]
        before_picking = picking.read(['state', 'scheduled_date', 'date_done', 'printed'])[0]
        before_moves = picking.move_ids.read(['sale_line_id', 'state', 'quantity', 'product_uom_qty'])
        report_values = self.report_model._get_report_values([picking.id])
        self.assertEqual(report_values['conduce_documents'][0]['sale'], sale)
        conduce = self.env['fcr.vehicle.conduce'].browse(
            picking.action_open_vehicle_conduce_outgoing()['res_id']
        )
        self.assertEqual(conduce.vehicle_id, values['vehicle'])
        self.assertEqual(conduce.partner_id, self.recipient)
        self.assertEqual(sale.read(['partner_id', 'partner_shipping_id', 'state', 'amount_total'])[0], before_sale)
        self.assertEqual(picking.read(['state', 'scheduled_date', 'date_done', 'printed'])[0], before_picking)
        self.assertEqual(picking.move_ids.read(['sale_line_id', 'state', 'quantity', 'product_uom_qty']), before_moves)

    def test_sale_resolution_accepts_multiple_relations_to_same_sale(self):
        picking, sale = self._picking()
        reference = self._stock_reference_for_sale(sale)
        picking.move_ids.reference_ids = [(4, reference.id)]
        self.assertEqual(picking._get_vehicle_conduce_outgoing_values()['sale'], sale)

    def test_conflicting_sale_relations_do_not_block_outgoing_conduce(self):
        picking, sale = self._picking()
        other_sale = self.env['sale.order'].create({
            'partner_id': self.customer.id,
            'partner_shipping_id': self.recipient.id,
        })
        reference = self._stock_reference_for_sale(other_sale)
        picking.move_ids.reference_ids = [(4, reference.id)]
        self.assertFalse(picking._get_vehicle_conduce_sale(picking._get_vehicle_conduce_moves()))
        values = picking._get_vehicle_conduce_outgoing_values()
        self.assertEqual(values['partner'], self.recipient)
        self.assertEqual(values['vehicle'], picking.move_ids.product_id.product_tmpl_id.vehicle_id)
        self.assertFalse(values['sale'])
        self.assertNotEqual(sale, other_sale)

    def test_origin_does_not_establish_sale(self):
        picking, sale = self._picking(linked=False)
        picking.origin = sale.name
        values = picking._get_vehicle_conduce_outgoing_values()
        self.assertFalse(values['sale'])
        self.assertEqual(values['partner'], self.recipient)

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

    def test_multiple_sale_contexts_are_ignored_when_not_needed(self):
        picking, sale = self._picking()
        other_sale = self.env['sale.order'].create({
            'partner_id': self.customer.id,
            'partner_shipping_id': self.recipient.id,
        })
        accessory = self.env['product.product'].create({'name': 'Accessory with other sale', 'type': 'consu'})
        other_line = self.env['sale.order.line'].create({'order_id': other_sale.id, 'product_id': accessory.id})
        self._move(picking, accessory, other_line)
        values = picking._get_vehicle_conduce_outgoing_values()
        self.assertFalse(values['sale'])
        self.assertEqual(values['partner'], self.recipient)
        self.assertNotEqual(sale, other_sale)

    def test_vehicle_move_without_sale_line_is_allowed_when_picking_has_sale_relation(self):
        picking, sale = self._picking(linked=False)
        reference = self._stock_reference_for_sale(sale)
        picking.move_ids.reference_ids = [(4, reference.id)]
        accessory = self.env['product.product'].create({'name': 'Accessory', 'type': 'consu'})
        line = self.env['sale.order.line'].create({'order_id': sale.id, 'product_id': accessory.id})
        self._move(picking, accessory, line)
        self.assertEqual(picking._get_vehicle_conduce_outgoing_values()['sale'], sale)

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

    def test_sale_line_product_mismatch_does_not_block_outgoing_conduce(self):
        picking, sale = self._picking()
        other_product, _vehicle = self._vehicle_product()
        other_line = self.env['sale.order.line'].create({'order_id': sale.id, 'product_id': other_product.id})
        picking.move_ids.sale_line_id = other_line
        values = picking._get_vehicle_conduce_outgoing_values()
        self.assertEqual(values['sale'], sale)
        self.assertEqual(values['vehicle'], picking.move_ids.product_id.product_tmpl_id.vehicle_id)

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

    def test_ready_receipt_contact_vehicle_purchase_and_scheduled_date(self):
        product, vehicle = self._vehicle_product()
        picking, purchase, vendor = self._purchase_picking([product])
        values = picking.with_context(tz='America/Santo_Domingo')._get_vehicle_conduce_incoming_values()
        self.assertEqual(values['purchase'], purchase)
        self.assertEqual(values['partner'], vendor)
        self.assertEqual(values['vehicle'], vehicle)
        self.assertEqual(values['date'], '28/06/2026')
        self.assertEqual(values['partner_label'], 'Recibido a')
        self.assertEqual(values['concept'], 'Adquisición FCR')
        self.assertEqual(picking._get_vehicle_conduce_entry_type(), 'purchase')

    def test_consignment_incoming_generates_without_purchase(self):
        product, vehicle = self._vehicle_product()
        picking, consignor = self._manual_incoming_picking([product])
        self.assertFalse(picking.purchase_id)
        values = picking.with_context(tz='America/Santo_Domingo')._get_vehicle_conduce_incoming_values()
        self.assertFalse(values['purchase'])
        self.assertEqual(values['partner'], consignor)
        self.assertEqual(values['vehicle'], vehicle)
        self.assertEqual(values['date'], '28/06/2026')
        self.assertEqual(values['partner_label'], 'Recibido a')
        self.assertEqual(values['concept'], 'Consignación')
        html, _kind = self.env['ir.actions.report']._render_qweb_html(
            self.incoming_report.report_name, picking.ids,
        )
        text = html_parser.fromstring(html).text_content()
        self.assertIn(consignor.name, text)
        self.assertIn('Consignación', text)
        conduce = self.env['fcr.vehicle.conduce'].browse(
            picking.action_open_vehicle_conduce_incoming()['res_id']
        )
        self.assertEqual(conduce.partner_id, consignor)
        self.assertEqual(conduce.vehicle_id, vehicle)

    def test_consignment_incoming_without_partner_rejected(self):
        picking, _consignor = self._manual_incoming_picking()
        picking.partner_id = False
        with self.assertRaisesRegex(UserError, 'contacto'):
            picking._get_vehicle_conduce_incoming_values()

    def test_consignment_incoming_without_vehicle_rejected(self):
        accessory = self.env['product.product'].create({'name': 'Consignment accessory only', 'type': 'consu'})
        picking, _consignor = self._manual_incoming_picking([accessory])
        with self.assertRaisesRegex(UserError, 'No hay un veh'):
            picking._get_vehicle_conduce_incoming_values()

    def test_consignment_incoming_multiple_vehicles_rejected(self):
        first = self._vehicle_product()[0]
        second = self._vehicle_product()[0]
        picking, _consignor = self._manual_incoming_picking([first, second])
        with self.assertRaisesRegex(UserError, 'varios veh'):
            picking._get_vehicle_conduce_incoming_values()

    def test_manual_receipt_not_marked_as_consignment_requires_purchase(self):
        picking, _consignor = self._manual_incoming_picking(entry_type='purchase')
        self.assertFalse(picking.purchase_id)
        with self.assertRaisesRegex(UserError, 'compra'):
            picking._get_vehicle_conduce_incoming_values()

    def test_picking_signature_fields_exist_and_store(self):
        picking, _sale = self._picking()
        for field_name in (
            'vehicle_conduce_inspector_name',
            'vehicle_conduce_inspector_signature',
            'vehicle_conduce_customer_name',
            'vehicle_conduce_customer_signature',
        ):
            self.assertIn(field_name, picking._fields)
        self._sign_picking(picking)
        picking.invalidate_recordset()
        self.assertEqual(picking.vehicle_conduce_inspector_name, 'Inspector Tablet')
        self.assertEqual(picking.vehicle_conduce_customer_name, 'Cliente Tablet')
        self.assertTrue(picking.vehicle_conduce_inspector_signature)
        self.assertTrue(picking.vehicle_conduce_customer_signature)

    def test_outgoing_report_values_use_picking_signatures(self):
        picking, _sale = self._picking()
        self._sign_picking(picking, inspector='Inspector Salida', customer='Cliente Salida')
        conduce = self.env['fcr.vehicle.conduce'].browse(
            picking.action_open_vehicle_conduce_outgoing()['res_id']
        )
        values = conduce._get_pdf_values()
        self.assertEqual(values['inspector_name'], 'Inspector Salida')
        self.assertEqual(values['client_name'], 'Cliente Salida')
        self.assertEqual(values['inspector_signature'], picking.vehicle_conduce_inspector_signature)
        self.assertEqual(values['client_signature'], picking.vehicle_conduce_customer_signature)

    def test_purchase_incoming_report_values_use_picking_signatures(self):
        picking, _purchase, _vendor = self._purchase_picking()
        self._sign_picking(picking, inspector='Inspector Compra', customer='Proveedor Firmante')
        conduce = self.env['fcr.vehicle.conduce'].browse(
            picking.action_open_vehicle_conduce_incoming()['res_id']
        )
        values = conduce._get_pdf_values()
        self.assertEqual(values['inspector_name'], 'Inspector Compra')
        self.assertEqual(values['client_name'], 'Proveedor Firmante')
        self.assertEqual(values['inspector_signature'], picking.vehicle_conduce_inspector_signature)
        self.assertEqual(values['client_signature'], picking.vehicle_conduce_customer_signature)

    def test_consignment_incoming_report_values_use_picking_signatures(self):
        picking, consignor = self._manual_incoming_picking()
        self._sign_picking(picking, inspector='Inspector Consigna', customer='Propietario Consigna')
        values = self.env['fcr.vehicle.conduce'].browse(
            picking.action_open_vehicle_conduce_incoming()['res_id']
        )._get_pdf_values()
        self.assertEqual(values['partner'], consignor)
        self.assertEqual(values['concept'], 'Consignación')
        self.assertEqual(values['inspector_name'], 'Inspector Consigna')
        self.assertEqual(values['client_name'], 'Propietario Consigna')

    def test_report_generates_without_picking_signatures(self):
        picking, _sale = self._picking()
        values = self.report_model._get_report_values([picking.id])['conduce_documents'][0]
        self.assertFalse(values['inspector_signature'])
        self.assertFalse(values['client_signature'])
        self.assertEqual(values['client_name'], self.recipient.name)

    def test_saving_picking_signatures_does_not_change_inventory(self):
        picking, _sale = self._picking()
        before_picking = picking.read(['state', 'scheduled_date', 'date_done', 'printed'])[0]
        before_moves = picking.move_ids.read(['state', 'quantity', 'product_uom_qty'])
        quant_domain = [('product_id', 'in', picking.move_ids.product_id.ids)]
        before_quants = self.env['stock.quant'].search(quant_domain).read(['quantity', 'reserved_quantity'])
        self._sign_picking(picking)
        self.assertEqual(picking.read(['state', 'scheduled_date', 'date_done', 'printed'])[0], before_picking)
        self.assertEqual(picking.move_ids.read(['state', 'quantity', 'product_uom_qty']), before_moves)
        self.assertEqual(self.env['stock.quant'].search(quant_domain).read(['quantity', 'reserved_quantity']), before_quants)

    def test_report_uses_stored_picking_signature_names_after_partner_change(self):
        picking, _sale = self._picking()
        self._sign_picking(picking, inspector='Inspector Guardado', customer='Cliente Guardado')
        self.recipient.name = 'Cliente cambiado después de firmar'
        values = self.env['fcr.vehicle.conduce'].browse(
            picking.action_open_vehicle_conduce_outgoing()['res_id']
        )._get_pdf_values()
        self.assertEqual(values['inspector_name'], 'Inspector Guardado')
        self.assertEqual(values['client_name'], 'Cliente Guardado')
        self.assertNotEqual(values['client_name'], self.recipient.name)

    def test_qweb_html_renders_picking_signatures(self):
        picking, _sale = self._picking()
        self._sign_picking(picking, inspector='Inspector HTML', customer='Cliente HTML')
        html, _kind = self.env['ir.actions.report']._render_qweb_html(self.report.report_name, picking.ids)
        html_text = html.decode()
        self.assertIn('Inspector HTML', html_text)
        self.assertIn('Cliente HTML', html_text)
        self.assertIn('data:image', html_text)

    def test_incoming_contact_fallback_and_empty_fields(self):
        picking, purchase, vendor = self._purchase_picking()
        picking.partner_id = False
        vendor.write({'phone': False, 'email': False, 'vat': False})
        values = picking._get_vehicle_conduce_incoming_values()
        self.assertEqual(values['partner'], purchase.partner_id)
        html, _kind = self.env['ir.actions.report']._render_qweb_html(
            self.incoming_report.report_name, picking.ids,
        )
        text = html_parser.fromstring(html).text_content()
        self.assertIn(vendor.name, text)
        self.assertIn('Adquisición FCR', text)

    def test_origin_does_not_establish_purchase(self):
        product = self._vehicle_product()[0]
        picking = self.env['stock.picking'].create({
            'picking_type_id': self.warehouse.in_type_id.id,
            'partner_id': self.customer.id,
            'location_id': self.env.ref('stock.stock_location_suppliers').id,
            'location_dest_id': self.warehouse.lot_stock_id.id,
        })
        self._move(picking, product)
        picking.origin = 'P00001'
        picking.scheduled_date = datetime(2026, 6, 28, 16, 0)
        with self.assertRaisesRegex(UserError, 'compra'):
            picking._get_vehicle_conduce_incoming_values()

    def test_outgoing_rejected_by_incoming_and_incoming_rejected_by_outgoing(self):
        outgoing, _sale = self._picking()
        incoming, _purchase, _vendor = self._purchase_picking()
        with self.assertRaisesRegex(UserError, 'operaciones de entrada'):
            outgoing._get_vehicle_conduce_incoming_values()
        with self.assertRaisesRegex(UserError, 'operaciones de salida'):
            incoming._get_vehicle_conduce_outgoing_values()

    def test_incoming_not_ready_rejected(self):
        picking, _purchase, _vendor = self._purchase_picking()
        picking.move_ids.state = 'confirmed'
        with self.assertRaisesRegex(UserError, 'Lista o Hecha'):
            picking._get_vehicle_conduce_incoming_values()

    def test_incoming_missing_vehicle_rejected(self):
        product = self.env['product.product'].create({'name': 'Receipt accessory only', 'type': 'consu'})
        picking, _purchase, _vendor = self._purchase_picking([product])
        with self.assertRaisesRegex(UserError, 'No hay un vehículo'):
            picking._get_vehicle_conduce_incoming_values()
        product.is_fleet = True
        with self.assertRaisesRegex(UserError, 'sin vínculo'):
            picking._get_vehicle_conduce_incoming_values()

    def test_incoming_multiple_vehicles_rejected(self):
        first = self._vehicle_product()[0]
        second = self._vehicle_product()[0]
        picking, _purchase, _vendor = self._purchase_picking([first, second])
        with self.assertRaisesRegex(UserError, 'varios vehículos'):
            picking._get_vehicle_conduce_incoming_values()

    def test_incoming_accessory_does_not_count_as_vehicle(self):
        vehicle_product, vehicle = self._vehicle_product()
        accessory = self.env['product.product'].create({'name': 'Receipt accessory', 'type': 'consu'})
        picking, _purchase, _vendor = self._purchase_picking([vehicle_product, accessory])
        self.assertEqual(picking._get_vehicle_conduce_incoming_values()['vehicle'], vehicle)
        accessory.is_fleet = True
        with self.assertRaisesRegex(UserError, 'sin vínculo'):
            picking._get_vehicle_conduce_incoming_values()

    def test_incoming_done_date_and_timezone(self):
        picking, _purchase, _vendor = self._purchase_picking()
        picking.move_ids.write({'quantity': 1, 'state': 'done'})
        picking.date_done = datetime(2026, 7, 2, 1, 0)
        values = picking.with_context(tz='America/Santo_Domingo')._get_vehicle_conduce_incoming_values()
        self.assertEqual(values['date'], '01/07/2026')
        picking.date_done = False
        with self.assertRaisesRegex(UserError, 'fecha efectiva'):
            picking._get_vehicle_conduce_incoming_values()

    def test_incoming_qweb_html_and_escaping(self):
        picking, _purchase, vendor = self._purchase_picking()
        vendor.name = '<script>alert("entrada")</script> Proveedor & Asociados'
        vehicle = picking.move_ids.product_id.product_tmpl_id.vehicle_id
        vehicle.vin_sn = 'INVIN' + '1234567890' * 4
        html, _kind = self.env['ir.actions.report']._render_qweb_html(
            self.incoming_report.report_name, picking.ids,
        )
        html_text = html.decode()
        document = html_parser.fromstring(html_text)
        content = document.xpath('//div[contains(@class, "fcr-content")]')[0]
        self.assertIn('CONDUCE DE ENTRADA', html_text)
        self.assertIn('vehicle_inspection_drawings.png', html_text)
        self.assertIn('Acogiéndome', html_text)
        self.assertFalse(content.xpath('.//script'))
        self.assertIn(vendor.name, content.text_content())
        self.assertIn(vehicle.vin_sn, content.text_content())

    def test_incoming_report_rejects_mixed_batch_and_missing_ids(self):
        valid, _purchase, _vendor = self._purchase_picking()
        invalid, _sale = self._picking()
        with self.assertRaises(UserError):
            self.incoming_report_model._get_report_values((valid | invalid).ids)
        with self.assertRaises(UserError):
            self.incoming_report_model._get_report_values([])
        documents = self.incoming_report_model._get_report_values([valid.id, valid.id])
        self.assertEqual(len(documents['conduce_documents']), 1)

    def test_report_rejects_mixed_batch_and_missing_ids(self):
        valid, _sale = self._picking()
        invalid, _sale = self._picking(picking_type=self.warehouse.in_type_id)
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
        no_sale, _sale = self._picking(linked=False)
        self.assertIn(self.report.id, self.report.get_valid_action_reports('stock.picking', no_sale.ids))
        reference_only, sale = self._picking(linked=False)
        reference = self._stock_reference_for_sale(sale)
        reference_only.move_ids.reference_ids = [(4, reference.id)]
        self.assertIn(
            self.report.id,
            self.report.get_valid_action_reports('stock.picking', reference_only.ids),
        )
        picking.move_ids.state = 'cancel'
        self.assertNotIn(self.report.id, self.report.get_valid_action_reports('stock.picking', picking.ids))
        receipt, _purchase, _vendor = self._purchase_picking()
        self.assertIn(
            self.incoming_report.id,
            self.incoming_report.get_valid_action_reports('stock.picking', receipt.ids),
        )
        consignment, _consignor = self._manual_incoming_picking()
        self.assertIn(
            self.incoming_report.id,
            self.incoming_report.get_valid_action_reports('stock.picking', consignment.ids),
        )
        manual_purchase, _consignor = self._manual_incoming_picking(entry_type='purchase')
        self.assertNotIn(
            self.incoming_report.id,
            self.incoming_report.get_valid_action_reports('stock.picking', manual_purchase.ids),
        )
        receipt.move_ids.state = 'cancel'
        self.assertNotIn(
            self.incoming_report.id,
            self.incoming_report.get_valid_action_reports('stock.picking', receipt.ids),
        )
        self.assertEqual(self.report.paperformat_id.format, 'Letter')
        self.assertEqual(self.incoming_report.paperformat_id, self.report.paperformat_id)
        self.assertAlmostEqual(self.report.paperformat_id.print_page_width, 215.9)
        self.assertAlmostEqual(self.report.paperformat_id.print_page_height, 279.4)

    def test_report_binding_and_standard_reports_are_independent(self):
        for report in (self.report, self.incoming_report):
            with self.subTest(report=report.name):
                self.assertEqual(report.model, 'stock.picking')
                self.assertEqual(report.binding_model_id.model, 'stock.picking')
                self.assertEqual(report.binding_type, 'report')
                self.assertEqual(set(report.binding_view_types.split(',')), {'list', 'form'})
        bindings = self.env['ir.actions.actions'].get_bindings('stock.picking')['report']
        self.assertIn(self.report.id, [action['id'] for action in bindings])
        self.assertIn(self.incoming_report.id, [action['id'] for action in bindings])
        for xmlid, template in (
            ('stock.action_report_delivery', 'stock.report_deliveryslip'),
            ('stock.action_report_picking', 'stock.report_picking'),
        ):
            standard = self.env.ref(xmlid)
            self.assertNotEqual(standard, self.report)
            self.assertEqual(standard.model, 'stock.picking')
            self.assertEqual(standard.report_name, template)
            self.assertEqual(standard.report_type, 'qweb-pdf')
            self.assertIn(standard.id, [action['id'] for action in bindings])

    def test_form_has_separate_conditional_conduce_button(self):
        view = self.env['stock.picking'].get_view(
            view_id=self.env.ref('stock.view_picking_form').id, view_type='form',
        )
        form = html_parser.fromstring(view['arch'])
        outgoing_buttons = form.xpath('//header/button[@name="%s"]' % self.report.id)
        incoming_buttons = form.xpath('//header/button[@name="%s"]' % self.incoming_report.id)
        outgoing_checklist_buttons = form.xpath('//header/button[@name="action_open_vehicle_conduce_outgoing"]')
        incoming_checklist_buttons = form.xpath('//header/button[@name="action_open_vehicle_conduce_incoming"]')
        self.assertEqual(len(outgoing_buttons), 1)
        self.assertEqual(len(incoming_buttons), 1)
        self.assertEqual(len(outgoing_checklist_buttons), 1)
        self.assertEqual(len(incoming_checklist_buttons), 1)
        self.assertEqual(outgoing_buttons[0].get('type'), 'action')
        self.assertEqual(incoming_buttons[0].get('type'), 'action')
        self.assertEqual(outgoing_checklist_buttons[0].get('type'), 'object')
        self.assertEqual(incoming_checklist_buttons[0].get('type'), 'object')
        self.assertTrue(form.xpath('//field[@name="sale_id"]'))
        self.assertTrue(form.xpath('//field[@name="purchase_id"]'))
        self.assertTrue(form.xpath('//field[@name="vehicle_entry_type"]'))
        self.assertTrue(form.xpath('//page[@string="Firmas Conduce"]'))
        self.assertTrue(form.xpath('//field[@name="vehicle_conduce_inspector_name"]'))
        self.assertTrue(form.xpath('//field[@name="vehicle_conduce_inspector_signature"][@widget="signature"]'))
        self.assertTrue(form.xpath('//field[@name="vehicle_conduce_customer_name"]'))
        self.assertTrue(form.xpath('//field[@name="vehicle_conduce_customer_signature"][@widget="signature"]'))
        # Both standard Print buttons must remain present and keep their targets.
        self.assertTrue(form.xpath('//header/button[@name="do_print_picking"][@type="object"]'))
        standard_id = self.env.ref('stock.action_report_delivery').id
        self.assertTrue(form.xpath('//header/button[@name="%s"][@type="action"]' % standard_id))
        outgoing_condition = outgoing_buttons[0].get('invisible')
        incoming_condition = incoming_buttons[0].get('invisible')
        outgoing_checklist_condition = outgoing_checklist_buttons[0].get('invisible')
        incoming_checklist_condition = incoming_checklist_buttons[0].get('invisible')
        for state in ('draft', 'waiting', 'confirmed', 'assigned', 'done', 'cancel'):
            for code in ('incoming', 'internal', 'outgoing'):
                for sale_id in (False, 1):
                    for purchase_id in (False, 1):
                        for vehicle_entry_type in ('purchase', 'consignment'):
                            with self.subTest(
                                state=state, code=code, sale_id=sale_id,
                                purchase_id=purchase_id, vehicle_entry_type=vehicle_entry_type,
                            ):
                                eval_context = {
                                    'id': 1, 'state': state, 'picking_type_code': code,
                                    'sale_id': sale_id, 'purchase_id': purchase_id,
                                    'vehicle_entry_type': vehicle_entry_type,
                                }
                                outgoing_visible = not safe_eval(outgoing_condition, eval_context)
                                incoming_visible = not safe_eval(incoming_condition, eval_context)
                                outgoing_checklist_visible = not safe_eval(outgoing_checklist_condition, eval_context)
                                incoming_checklist_visible = not safe_eval(incoming_checklist_condition, eval_context)
                                expected_outgoing = code == 'outgoing' and state in ('assigned', 'done')
                                expected_incoming = (
                                    code == 'incoming'
                                    and state in ('assigned', 'done')
                                    and (purchase_id or vehicle_entry_type == 'consignment')
                                )
                                self.assertEqual(outgoing_visible, expected_outgoing)
                                self.assertEqual(incoming_visible, expected_incoming)
                                self.assertEqual(outgoing_checklist_visible, outgoing_visible)
                                self.assertEqual(incoming_checklist_visible, incoming_visible)

    def test_incoming_conduce_action_invocation_in_assigned_and_done(self):
        picking, _purchase, _vendor = self._purchase_picking()
        for state in ('assigned', 'done'):
            if state == 'done':
                picking.move_ids.write({'quantity': 1, 'state': 'done'})
                picking.date_done = datetime(2026, 7, 2, 16)
            with self.subTest(state=state):
                self.assertEqual(picking.state, state)
                action = self.incoming_report.report_action(picking, config=False)
                self.assertEqual(action['type'], 'ir.actions.report')
                self.assertEqual(action['report_name'], self.incoming_report.report_name)
                html, _kind = self.env['ir.actions.report']._render_qweb_html(action['report_name'], picking.ids)
                self.assertIn(b'CONDUCE DE ENTRADA', html)
                self.assertEqual(picking.state, state)

    def test_incoming_printing_does_not_change_inventory(self):
        first, _purchase, _vendor = self._purchase_picking()
        second, _consignor = self._manual_incoming_picking()
        pickings = first | second
        before_pickings = pickings.read(['state', 'scheduled_date', 'date_done', 'printed'])
        before_moves = pickings.move_ids.read(['state', 'quantity', 'product_uom_qty'])
        quant_domain = [('product_id', 'in', pickings.move_ids.product_id.ids)]
        before_quants = self.env['stock.quant'].search(quant_domain).read(['quantity', 'reserved_quantity'])
        action = self.incoming_report.report_action(pickings, config=False)
        html, _kind = self.env['ir.actions.report']._render_qweb_html(action['report_name'], pickings.ids)
        document = html_parser.fromstring(html)
        self.assertEqual(len(document.xpath('//div[contains(@class, "fcr-conduce-article")]')), 2)
        self.assertEqual(pickings.read(['state', 'scheduled_date', 'date_done', 'printed']), before_pickings)
        self.assertEqual(pickings.move_ids.read(['state', 'quantity', 'product_uom_qty']), before_moves)
        self.assertEqual(self.env['stock.quant'].search(quant_domain).read(['quantity', 'reserved_quantity']), before_quants)

    def test_create_outgoing_digital_conduce_from_valid_delivery(self):
        picking, _sale = self._picking()
        vehicle = picking.move_ids.product_id.product_tmpl_id.vehicle_id
        action = picking.action_open_vehicle_conduce_outgoing()
        conduce = self.env['fcr.vehicle.conduce'].browse(action['res_id'])
        self.assertEqual(action['res_model'], 'fcr.vehicle.conduce')
        self.assertEqual(conduce.picking_id, picking)
        self.assertEqual(conduce.conduce_type, 'outgoing')
        self.assertEqual(conduce.vehicle_id, vehicle)
        self.assertEqual(conduce.partner_id, self.recipient)
        self.assertEqual(conduce.state, 'draft')
        self.assertEqual(conduce.inspector_id, self.env.user)

    def test_create_incoming_digital_conduce_from_valid_receipt(self):
        picking, _purchase, vendor = self._purchase_picking()
        vehicle = picking.move_ids.product_id.product_tmpl_id.vehicle_id
        action = picking.action_open_vehicle_conduce_incoming()
        conduce = self.env['fcr.vehicle.conduce'].browse(action['res_id'])
        self.assertEqual(action['res_model'], 'fcr.vehicle.conduce')
        self.assertEqual(conduce.picking_id, picking)
        self.assertEqual(conduce.conduce_type, 'incoming')
        self.assertEqual(conduce.vehicle_id, vehicle)
        self.assertEqual(conduce.partner_id, vendor)
        self.assertEqual(conduce.state, 'draft')

    def test_same_vehicle_can_have_independent_incoming_and_outgoing_conduces(self):
        product, vehicle = self._vehicle_product()
        incoming, _purchase, _vendor = self._purchase_picking([product])
        outgoing, _sale = self._picking(product)
        incoming_conduce = self.env['fcr.vehicle.conduce'].browse(
            incoming.action_open_vehicle_conduce_incoming()['res_id']
        )
        outgoing_conduce = self.env['fcr.vehicle.conduce'].browse(
            outgoing.action_open_vehicle_conduce_outgoing()['res_id']
        )
        self.assertNotEqual(incoming_conduce, outgoing_conduce)
        self.assertEqual(incoming_conduce.vehicle_id, vehicle)
        self.assertEqual(outgoing_conduce.vehicle_id, vehicle)
        self.assertEqual(incoming_conduce.conduce_type, 'incoming')
        self.assertEqual(outgoing_conduce.conduce_type, 'outgoing')

    def test_same_vehicle_can_have_multiple_operation_conduces(self):
        product, vehicle = self._vehicle_product()
        first, _sale = self._picking(product)
        second, _sale = self._picking(product)
        first_conduce = self.env['fcr.vehicle.conduce'].browse(
            first.action_open_vehicle_conduce_outgoing()['res_id']
        )
        second_conduce = self.env['fcr.vehicle.conduce'].browse(
            second.action_open_vehicle_conduce_outgoing()['res_id']
        )
        self.assertNotEqual(first_conduce, second_conduce)
        self.assertEqual(first_conduce.vehicle_id, vehicle)
        self.assertEqual(second_conduce.vehicle_id, vehicle)

    def test_second_click_returns_same_digital_conduce(self):
        outgoing, _sale = self._picking()
        first = outgoing.action_open_vehicle_conduce_outgoing()['res_id']
        second = outgoing.action_open_vehicle_conduce_outgoing()['res_id']
        self.assertEqual(first, second)
        self.assertEqual(self.env['fcr.vehicle.conduce'].search_count([
            ('picking_id', '=', outgoing.id),
            ('conduce_type', '=', 'outgoing'),
        ]), 1)
        incoming, _purchase, _vendor = self._purchase_picking()
        first = incoming.action_open_vehicle_conduce_incoming()['res_id']
        second = incoming.action_open_vehicle_conduce_incoming()['res_id']
        self.assertEqual(first, second)
        self.assertEqual(self.env['fcr.vehicle.conduce'].search_count([
            ('picking_id', '=', incoming.id),
            ('conduce_type', '=', 'incoming'),
        ]), 1)

    def test_digital_conduce_rejects_wrong_picking_type(self):
        outgoing, _sale = self._picking()
        incoming, _purchase, _vendor = self._purchase_picking()
        with self.assertRaisesRegex(UserError, 'operaciones de entrada'):
            outgoing.action_open_vehicle_conduce_incoming()
        with self.assertRaisesRegex(UserError, 'operaciones de salida'):
            incoming.action_open_vehicle_conduce_outgoing()

    def test_digital_checklist_persists_and_completion_does_not_change_stock(self):
        picking, _purchase, _vendor = self._purchase_picking()
        product = picking.move_ids.product_id
        vehicle = picking._get_vehicle_conduce_incoming_values()['vehicle']
        before_picking = picking.read(['state', 'scheduled_date', 'date_done', 'printed'])
        before_moves = picking.move_ids.read(['state', 'quantity', 'product_uom_qty'])
        before_vehicle = vehicle.read(['product_id', 'product_tmpl_id', 'license_plate', 'vin_sn'])[0]
        before_product = product.read(['product_tmpl_id', 'qty_available', 'virtual_available'])[0]
        before_template = product.product_tmpl_id.read(['is_fleet', 'vehicle_id'])[0]
        quant_domain = [('product_id', 'in', picking.move_ids.product_id.ids)]
        before_quants = self.env['stock.quant'].search(quant_domain).read(['quantity', 'reserved_quantity'])
        conduce = self.env['fcr.vehicle.conduce'].browse(
            picking.action_open_vehicle_conduce_incoming()['res_id']
        )
        conduce.write({
            'check_lights': True,
            'check_radio': True,
            'check_spare_tire': True,
            'check_jack': True,
        })
        self._sign_conduce(conduce)
        conduce.action_mark_completed()
        conduce.invalidate_recordset()
        self.assertTrue(conduce.check_lights)
        self.assertTrue(conduce.check_radio)
        self.assertTrue(conduce.check_spare_tire)
        self.assertTrue(conduce.check_jack)
        self.assertEqual(conduce.state, 'done')
        self.assertEqual(conduce.completed_by_id, self.env.user)
        self.assertTrue(conduce.completed_date)
        self.assertTrue(conduce.inspector_signed_at)
        self.assertTrue(conduce.client_signed_at)
        self.assertEqual(conduce.snapshot_partner_name, conduce.partner_id.name)
        self.assertEqual(conduce.snapshot_vehicle_vin_sn, vehicle.vin_sn)
        self.assertTrue(conduce.snapshot_check_lights)
        self.assertTrue(conduce.snapshot_check_radio)
        self.assertEqual(picking.read(['state', 'scheduled_date', 'date_done', 'printed']), before_picking)
        self.assertEqual(picking.move_ids.read(['state', 'quantity', 'product_uom_qty']), before_moves)
        self.assertEqual(vehicle.read(['product_id', 'product_tmpl_id', 'license_plate', 'vin_sn'])[0], before_vehicle)
        self.assertEqual(product.read(['product_tmpl_id', 'qty_available', 'virtual_available'])[0], before_product)
        self.assertEqual(product.product_tmpl_id.read(['is_fleet', 'vehicle_id'])[0], before_template)
        self.assertEqual(self.env['stock.quant'].search(quant_domain).read(['quantity', 'reserved_quantity']), before_quants)

    def test_checklist_columns_cover_all_check_fields_in_order(self):
        Conduce = self.env['fcr.vehicle.conduce']
        self.assertEqual(len(Conduce._get_checklist_fields()), 39)
        configured_fields = [
            field_name
            for _title, field_names in Conduce.CHECKLIST_COLUMNS
            for field_name in field_names
        ]
        self.assertEqual(configured_fields, list(Conduce._get_checklist_fields()))
        for field_name in Conduce._get_checklist_fields():
            self.assertIn(field_name, Conduce._fields)
        # Coordinates are kept for backward compatibility but are no longer used by the PDF template.
        self.assertEqual(set(Conduce._get_checklist_fields()), set(Conduce._get_checklist_mark_coordinates()))
        Conduce._validate_checklist_mark_mapping()

    def test_pdf_checklist_columns_reflect_saved_booleans(self):
        picking, _sale = self._picking()
        conduce = self.env['fcr.vehicle.conduce'].browse(
            picking.action_open_vehicle_conduce_outgoing()['res_id']
        )
        conduce.write({'check_lights': True, 'check_radio': False, 'check_keys': True})
        items = {
            item['field']: item
            for column in conduce._get_pdf_values()['checklist_columns']
            for item in column['items']
        }
        self.assertTrue(items['check_lights']['checked'])
        self.assertTrue(items['check_keys']['checked'])
        self.assertFalse(items['check_radio']['checked'])
        self.assertEqual(items['check_lights']['label'], 'Luces')

    def test_completion_requires_both_signatures(self):
        picking, _sale = self._picking()
        conduce = self.env['fcr.vehicle.conduce'].browse(
            picking.action_open_vehicle_conduce_outgoing()['res_id']
        )
        with self.assertRaisesRegex(UserError, 'firma del inspector'):
            conduce.action_mark_completed()
        conduce.inspector_signature = self._signature('inspector')
        with self.assertRaisesRegex(UserError, 'firma del cliente'):
            conduce.action_mark_completed()

    def test_completed_pdf_uses_snapshot_not_live_records(self):
        picking, _sale = self._picking()
        conduce = self.env['fcr.vehicle.conduce'].browse(
            picking.action_open_vehicle_conduce_outgoing()['res_id']
        )
        conduce.write({'check_lights': True})
        self._sign_conduce(conduce)
        draft_values = conduce._get_pdf_values()
        self.assertEqual(draft_values['partner_name'], self.recipient.name)
        conduce.action_mark_completed()
        snapshot_partner = conduce.snapshot_partner_name
        snapshot_vin = conduce.snapshot_vehicle_vin_sn
        self.recipient.name = 'Changed recipient after done'
        conduce.vehicle_id.vin_sn = 'CHANGEDVINAFTERDONE'
        final_values = conduce._get_pdf_values()
        self.assertEqual(final_values['partner_name'], snapshot_partner)
        self.assertEqual(final_values['vehicle_vin_sn'], snapshot_vin)
        self.assertNotEqual(final_values['partner_name'], self.recipient.name)
        self.assertNotEqual(final_values['vehicle_vin_sn'], conduce.vehicle_id.vin_sn)
        self.assertTrue({item['field']: item for column in final_values['checklist_columns'] for item in column['items']}['check_lights']['checked'])

    def test_completed_digital_conduce_is_immutable(self):
        picking, _sale = self._picking()
        conduce = self.env['fcr.vehicle.conduce'].browse(
            picking.action_open_vehicle_conduce_outgoing()['res_id']
        )
        conduce.write({'check_lights': True})
        self._sign_conduce(conduce)
        conduce.action_mark_completed()
        with self.assertRaisesRegex(UserError, 'completado'):
            conduce.write({'check_radio': True})
        with self.assertRaisesRegex(UserError, 'completado'):
            conduce.write({'state': 'draft'})

    def test_digital_conduce_must_be_completed_with_button(self):
        picking, _sale = self._picking()
        conduce = self.env['fcr.vehicle.conduce'].browse(
            picking.action_open_vehicle_conduce_outgoing()['res_id']
        )
        with self.assertRaisesRegex(UserError, 'botón Completar'):
            conduce.write({'state': 'done'})
        values = picking._get_vehicle_conduce_outgoing_values()
        with self.assertRaisesRegex(UserError, 'botón Completar'):
            self.env['fcr.vehicle.conduce'].create({
                'picking_id': picking.id,
                'conduce_type': 'outgoing',
                'vehicle_id': values['vehicle'].id,
                'partner_id': values['partner'].id,
                'date': values['date_raw'],
                'state': 'done',
            })

    def test_completion_revalidates_transfer(self):
        picking, _sale = self._picking()
        conduce = self.env['fcr.vehicle.conduce'].browse(
            picking.action_open_vehicle_conduce_outgoing()['res_id']
        )
        self._sign_conduce(conduce)
        other_product, _other_vehicle = self._vehicle_product()
        picking.move_ids.product_id.product_tmpl_id.vehicle_id = other_product.product_tmpl_id.vehicle_id
        with self.assertRaisesRegex(UserError, 'ya no coincide'):
            conduce.action_mark_completed()

    def test_digital_conduce_reuses_vehicle_validation(self):
        picking, _sale = self._picking()
        company = self.env['res.company'].create({'name': 'Other digital conduce company'})
        picking.move_ids.product_id.product_tmpl_id.vehicle_id.company_id = company
        with self.assertRaisesRegex(UserError, 'otra compañía'):
            picking.action_open_vehicle_conduce_outgoing()
        vehicle_product, vehicle = self._vehicle_product()
        accessory = self.env['product.product'].create({'name': 'Digital accessory', 'type': 'consu'})
        receipt, _purchase, _vendor = self._purchase_picking([vehicle_product, accessory])
        conduce = self.env['fcr.vehicle.conduce'].browse(
            receipt.action_open_vehicle_conduce_incoming()['res_id']
        )
        self.assertEqual(conduce.vehicle_id, vehicle)

    def test_direct_report_render_rejects_invalid_pickings(self):
        no_sale, _sale = self._picking(linked=False)
        incoming, _sale = self._picking(picking_type=self.warehouse.in_type_id)
        product = self.env['product.product'].create({'name': 'Unlinked accessory', 'type': 'consu'})
        no_vehicle, _sale = self._picking(product)
        for picking in no_sale | incoming | no_vehicle:
            with self.subTest(picking=picking.id), self.assertRaises(UserError):
                self.env['ir.actions.report']._render_qweb_html(self.report.report_name, picking.ids)

    def test_direct_incoming_report_render_rejects_invalid_pickings(self):
        outgoing, _sale = self._picking()
        no_purchase = self.env['stock.picking'].create({
            'picking_type_id': self.warehouse.in_type_id.id,
            'partner_id': self.customer.id,
            'location_id': self.env.ref('stock.stock_location_suppliers').id,
            'location_dest_id': self.warehouse.lot_stock_id.id,
        })
        no_purchase.scheduled_date = datetime(2026, 6, 28, 16, 0)
        self._move(no_purchase, self._vehicle_product()[0])
        accessory = self.env['product.product'].create({'name': 'Incoming accessory only', 'type': 'consu'})
        no_vehicle, _purchase, _vendor = self._purchase_picking([accessory])
        for picking in outgoing | no_purchase | no_vehicle:
            with self.subTest(picking=picking.id), self.assertRaises(UserError):
                self.env['ir.actions.report']._render_qweb_html(self.incoming_report.report_name, picking.ids)

    def test_conduce_action_invocation_in_assigned_and_done(self):
        picking, _sale = self._picking()
        for state in ('assigned', 'done'):
            if state == 'done':
                picking.move_ids.write({'quantity': 1, 'state': 'done'})
                picking.date_done = datetime(2026, 7, 2, 16)
            with self.subTest(state=state):
                self.assertEqual(picking.state, state)
                action = self.report.report_action(picking, config=False)
                self.assertEqual(action['type'], 'ir.actions.report')
                self.assertEqual(action['report_name'], self.report.report_name)
                html, _kind = self.env['ir.actions.report']._render_qweb_html(action['report_name'], picking.ids)
                self.assertIn(b'CONDUCE DE SALIDA', html)
                self.assertEqual(picking.state, state)

    def test_qweb_html_contains_vehicle_and_static_checklist(self):
        picking, _sale = self._picking()
        html, _kind = self.env['ir.actions.report']._render_qweb_html(self.report.report_name, picking.ids)
        html = html.decode()
        for text in ('CONDUCE DE SALIDA', 'TEST-CHASSIS', 'Conduce test recipient',
                     'vehicle_inspection_drawings.png', 'Luces', 'Relojes', 'Inspector',
                     'Cliente', 'No firme en caso de diferencia.'):
            self.assertIn(text, html)
        self.assertNotIn('fcr-checkmark', html)
        self.assertNotIn('position: absolute', html)

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
        before_pickings = pickings.read(['state', 'scheduled_date', 'date_done', 'printed'])
        before_moves = pickings.move_ids.read(['state', 'quantity', 'product_uom_qty'])
        quant_domain = [('product_id', 'in', pickings.move_ids.product_id.ids)]
        before_quants = self.env['stock.quant'].search(quant_domain).read(['quantity', 'reserved_quantity'])
        action = self.report.report_action(pickings, config=False)
        html, _kind = self.env['ir.actions.report']._render_qweb_html(action['report_name'], pickings.ids)
        document = html_parser.fromstring(html)
        self.assertEqual(len(document.xpath('//div[contains(@class, "fcr-conduce-article")]')), 2)
        self.assertEqual(pickings.read(['state', 'scheduled_date', 'date_done', 'printed']), before_pickings)
        self.assertEqual(pickings.move_ids.read(['state', 'quantity', 'product_uom_qty']), before_moves)
        self.assertEqual(self.env['stock.quant'].search(quant_domain).read(['quantity', 'reserved_quantity']), before_quants)
