from datetime import date

from odoo import fields
from odoo.tests import TransactionCase, tagged


@tagged("post_install", "-at_install")
class TestFcrSaleReceipt(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.currency = cls.env["res.currency"].with_context(active_test=False).search(
            [("name", "=", "DOP")], limit=1,
        )
        if not cls.currency:
            cls.currency = cls.env["res.currency"].create({
                "name": "DOP",
                "symbol": "RD$",
                "rounding": 0.01,
                "active": True,
            })
        else:
            cls.currency.active = True
        if cls.currency == cls.env.company.currency_id:
            cls.currency = cls.env["res.currency"].search([
                ("active", "=", True),
                ("id", "!=", cls.env.company.currency_id.id),
            ], limit=1)
        cls.pricelist = cls.env["product.pricelist"].create({
            "name": "FCR receipt test DOP",
            "currency_id": cls.currency.id,
            "company_id": cls.env.company.id,
        })
        cls.partner = cls.env["res.partner"].create({"name": "FCR receipt test customer"})
        cls.main_product = cls.env["product.product"].create({
            "name": "Primary vehicle line",
            "type": "consu",
            "list_price": 25000,
        })
        cls.main_product.product_tmpl_id.taxes_id = [(5, 0, 0)]
        cls.extra_product = cls.env["product.product"].create({
            "name": "Secondary product line",
            "type": "consu",
            "list_price": 1200,
        })
        cls.extra_product.product_tmpl_id.is_marbete = True
        cls.order = cls.env["sale.order"].create({
            "partner_id": cls.partner.id,
            "pricelist_id": cls.pricelist.id,
        })
        cls.main_line = cls.env["sale.order.line"].create({
            "order_id": cls.order.id,
            "product_id": cls.main_product.id,
            "name": "Primary vehicle line",
            "product_uom_qty": 1,
            "price_unit": 25000,
            "sequence": 10,
        })
        cls.env["sale.order.line"].create({
            "order_id": cls.order.id,
            "product_id": cls.extra_product.id,
            "name": "Secondary product line",
            "product_uom_qty": 1,
            "price_unit": 1200,
            "sequence": 1,
        })

    def _create_receipt_history(self, amount, receipt_date):
        return self.env["fcr.sale.receipt.history"].sudo().create({
            "sale_order_id": self.order.id,
            "receipt_date": receipt_date,
            "currency_id": self.currency.id,
            "amount": amount,
        })

    def test_receipt_values_accumulate_advances_and_use_primary_line(self):
        first_receipt = self._create_receipt_history(1000, date(2026, 10, 1))
        first_values = self.order._get_sale_receipt_values()

        self.assertEqual(first_values["total_cost"], 25000)
        self.assertEqual(first_values["advance_payment"], 1000)
        self.assertEqual(first_values["paid_before_current"], 0)
        self.assertEqual(first_values["paid_to_date"], 1000)
        self.assertEqual(first_values["balance"], 24000)

        second_receipt = self._create_receipt_history(5000, date(2026, 10, 5))
        second_values = self.order._get_sale_receipt_values()

        self.assertEqual(second_values["items_text"], "Primary vehicle line")
        self.assertEqual(second_values["total_cost"], 25000)
        self.assertEqual(second_values["advance_payment"], 5000)
        self.assertEqual(second_values["paid_before_current"], 1000)
        self.assertEqual(second_values["paid_to_date"], first_receipt.amount + second_receipt.amount)
        self.assertEqual(second_values["paid_to_date"], 6000)
        self.assertEqual(second_values["balance"], 19000)
        self.assertEqual(second_values["date_text"], "5 de Octubre del 2026")

    def test_new_receipt_defaults_to_today_not_previous_receipt_date(self):
        self.order.write({"fcr_receipt_date": date(2026, 9, 20)})

        action = self.env["fcr.sale.receipt.wizard"].action_open_for_document(self.order)
        wizard = self.env["fcr.sale.receipt.wizard"].browse(action["res_id"])

        self.assertEqual(wizard.receipt_date, fields.Date.context_today(self.env.user))

    def test_save_and_print_migrates_legacy_advance_and_records_current_advance(self):
        self.order.write({
            "fcr_receipt_amount": 2000,
            "fcr_receipt_date": date(2026, 9, 20),
        })
        wizard = self.env["fcr.sale.receipt.wizard"].create({
            "sale_order_id": self.order.id,
            "amount": 3500,
            "receipt_date": date(2026, 10, 7),
            "exchange_rate": 58.5,
        })

        action = wizard.action_save_and_print()
        history = self.order._get_sale_receipt_history_records()
        values = self.order._get_sale_receipt_values()

        self.assertEqual(action["type"], "ir.actions.report")
        self.assertEqual(len(history), 2)
        self.assertEqual(values["advance_payment"], 3500)
        self.assertEqual(values["paid_before_current"], 2000)
        self.assertEqual(values["paid_to_date"], 5500)
        self.assertEqual(values["balance"], self.main_line.price_total - 5500)
        self.assertIn("58.50", values["exchange_rate_text"])

    def test_invoice_receipt_uses_linked_order_total_and_history(self):
        prior = self._create_receipt_history(5000, date(2026, 10, 2))
        invoice = self.env["account.move"].create({
            "move_type": "out_invoice",
            "partner_id": self.partner.id,
            "invoice_line_ids": [(0, 0, {
                "product_id": self.main_product.id,
                "name": "Invoice vehicle line",
                "quantity": 1,
                "price_unit": 25000,
                "sale_line_ids": [(6, 0, [self.main_line.id])],
            })],
        })
        current = self.env["fcr.sale.receipt.history"].sudo().create({
            "sale_order_id": self.order.id,
            "invoice_id": invoice.id,
            "receipt_date": date(2026, 10, 8),
            "currency_id": self.currency.id,
            "amount": 7000,
            "exchange_rate": 58.75,
        })
        later_order_receipt = self._create_receipt_history(1200, date(2026, 10, 9))

        values = invoice._get_sale_receipt_values()

        self.assertEqual(values["items_text"], "Primary vehicle line")
        self.assertEqual(values["total_cost"], self.main_line.price_total)
        self.assertEqual(values["advance_payment"], later_order_receipt.amount)
        self.assertEqual(values["paid_before_current"], prior.amount + 7000)
        self.assertEqual(values["paid_to_date"], prior.amount + current.amount + later_order_receipt.amount)
        self.assertEqual(values["balance"], self.main_line.price_total - 13200)

    def test_sale_receipt_report_renders_html(self):
        self._create_receipt_history(3500, date(2026, 10, 7))
        html, output_type = self.env["ir.actions.report"]._render_qweb_html(
            "fcr_invoice_report.action_report_sale_separation_receipt",
            self.order.ids,
        )

        self.assertEqual(output_type, "html")
        self.assertIn(b"Total a pagar", html)
        self.assertIn(b"Avance de pago", html)
        self.assertIn(b"Pagado antes de este recibo", html)
        self.assertIn(b"Pagado a la fecha", html)
        self.assertIn(b"Pendiente por pagar", html)
        self.assertIn(b"Primary vehicle line", html)
        self.assertNotIn(b"Secondary product line", html)
