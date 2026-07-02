# -*- coding: utf-8 -*-

from odoo import fields
from odoo.exceptions import UserError, ValidationError
from odoo.tests import tagged, Form
from .test_ecf_common import TestL10nDoEcfCommon


@tagged('post_install_l10n', 'post_install', '-at_install')
class TestDoAccountMove(TestL10nDoEcfCommon):

    def test_l10n_do_out_invoice_default_values_form(self):
        """Test prueba campos computados y valores por defecto
        en formulario de Factura de cliente"""
        # self._setup_company_do()
        journal = self.journal_sale.copy({"name": "Invoices Journal"})
        form = self._l10n_do_create_form_move(
            move_type="out_invoice", internal_type="invoice", partner=self.partner_non_payer
        )
        self.assertIn(form.journal_id, journal + self.journal_sale)

    def test_l10n_do_out_ecf_invoice_final_consumer_limit_amount(self):
        """Test prueba monto maximo en Factura de cliente
        emitida a consumidor final"""
        # self._setup_company_do_ecf_contingency()
        self.product_a.list_price = 250001.00
        form = self._l10n_do_create_form_move(
            move_type="out_invoice",
            internal_type="invoice",
            partner=self.partner_non_payer,
        )

        with self.assertRaises(UserError):
            invoice = form.save()
            invoice.action_post()

    def test_l10n_do_out_ecf_invoice_e31(self):
        """"""
        # self._setup_company_do_ecf_contingency()
        ecf_fiscal_client = self.env.ref("l10n_do_accounting.ecf_fiscal_client")
        self.product_a.list_price = 250000.00
        form = self._l10n_do_create_form_move(
            move_type="out_invoice",
            internal_type="invoice",
            partner=self.partner_taxpayer,
        )
        invoice = form.save()
        invoice.action_post()

        self.assertEqual(invoice.state, "posted")
        self.assertEqual(invoice.l10n_do_ecf_send_state, "signed_pending")
        self.assertTrue(invoice.ecf_id)
        self.assertEqual(invoice.l10n_latam_document_type_id.internal_type, "invoice")
        self.assertEqual(invoice.ecf_id.l10n_latam_document_type_id, ecf_fiscal_client)
        return invoice

    def test_l10n_do_out_ecf_invoice_e32(self):
        """"""
        # self._setup_company_do_ecf_contingency()
        ecf_consumer_supplier = self.env.ref("l10n_do_accounting.ecf_consumer_supplier")
        self.product_a.list_price = 250.00
        form = self._l10n_do_create_form_move(
            move_type="out_invoice",
            internal_type="invoice",
            partner=self.partner_non_payer,
        )
        invoice = form.save()
        invoice.action_post()

        self.assertEqual(invoice.state, "posted")
        self.assertEqual(invoice.l10n_do_ecf_send_state, "signed_pending")
        self.assertTrue(invoice.ecf_id)
        self.assertEqual(invoice.l10n_latam_document_type_id.internal_type, "invoice")
        self.assertEqual(invoice.ecf_id.l10n_latam_document_type_id, ecf_consumer_supplier)

    def test_l10n_do_out_ecf_invoice_e31_foreign_currency(self):
        """Test prueba de Factura E31 en otra moneda."""
        # self._setup_company_do_ecf_contingency()
        currency_usd = self.env.ref('base.USD')
        currency_usd.active = True
        self.env['res.currency.rate'].create({
            'name': '2022-11-24',
            'company_id': self.company_data['company'].id,
            'currency_id': currency_usd.id,
            'rate': 0.016047474850})

        ecf_fiscal_client = self.env.ref("l10n_do_accounting.ecf_fiscal_client")
        self.product_a.list_price = 250000.00
        form = self._l10n_do_create_form_move(
            move_type="out_invoice",
            internal_type="invoice",
            currency_id=currency_usd,
            partner=self.partner_taxpayer,
        )
        invoice = form.save()
        invoice.action_post()

        self.assertEqual(invoice.state, "posted")
        self.assertEqual(invoice.l10n_do_ecf_send_state, "signed_pending")
        self.assertTrue(invoice.ecf_id)
        self.assertEqual(invoice.ecf_id.l10n_latam_document_type_id, ecf_fiscal_client)
        self.assertEqual(round(invoice.currency_rate, 2), 62.32)

    def test_l10n_do_out_ecf_invoice_e34(self):
        """"""
        # self._setup_company_do_ecf_contingency()
        ecf_fiscal_client = self.env.ref("l10n_do_accounting.ecf_credit_note_client")
        self.product_a.list_price = 250000.00
        invoice_origin = self.test_l10n_do_out_ecf_invoice_e31()
        form = self._l10n_do_create_form_move(
            move_type="out_refund",
            internal_type="credit_note",
            partner=self.partner_taxpayer,
        )
        invoice = form.save()
        invoice.l10n_do_origin_ncf = invoice_origin.l10n_latam_document_number
        invoice.l10n_do_ecf_date_modification = fields.Date.from_string('2025-11-25')
        invoice.l10n_do_ecf_modification_code = '1'
        invoice.action_post()

        self.assertEqual(invoice.state, "posted")
        self.assertEqual(invoice.l10n_do_ecf_send_state, "signed_pending")
        self.assertTrue(invoice.ecf_id)
        self.assertEqual(invoice.ecf_id.l10n_latam_document_type_id, ecf_fiscal_client)

    def test_l10n_do_out_ecf_invoice_e33(self):
        """"""
        # self._setup_company_do_ecf_contingency()
        ecf_debit_note_client = self.env.ref("l10n_do_accounting.ecf_debit_note_client")
        self.product_a.list_price = 250000.00
        invoice_origin = self.test_l10n_do_out_ecf_invoice_e31()
        form = self._l10n_do_create_form_move(
            move_type="out_invoice",
            internal_type="debit_note",
            partner=self.partner_taxpayer,
            latam_document_type=ecf_debit_note_client,
        )
        invoice = form.save()
        invoice.debit_origin_id = invoice_origin.id
        invoice.l10n_do_origin_ncf = invoice_origin.l10n_latam_document_number
        # invoice.l10n_cr_reason_ref = "Mercancia dañada"
        invoice.l10n_do_ecf_date_modification = fields.Date.from_string('2025-11-25')
        invoice.l10n_do_ecf_modification_code = '1'
        invoice.action_post()

        self.assertEqual(invoice.state, "posted")
        self.assertEqual(invoice.l10n_do_ecf_send_state, "signed_pending")
        self.assertTrue(invoice.ecf_id)
        self.assertEqual(invoice.l10n_latam_document_type_id, ecf_debit_note_client)

    def test_l10n_do_out_ecf_invoice_e41(self):
        """"""
        # self._setup_company_do_ecf_contingency()
        ecf_informal_supplier = self.env.ref("l10n_do_accounting.ecf_informal_supplier")
        self.product_a.list_price = 250000.00
        additional_context = {'default_l10n_do_expense_type': "1"}
        form = (self._l10n_do_create_form_move(
            move_type="in_invoice",
            internal_type="invoice",
            partner=self.partner_informal_supplier,
            latam_document_type=ecf_informal_supplier,
            additional_context=additional_context,
        ))
        invoice = form.save()
        invoice.action_post()

        self.assertEqual(invoice.state, "posted")
        self.assertEqual(invoice.l10n_do_ecf_send_state, "signed_pending")
        self.assertTrue(invoice.ecf_id)
        self.assertEqual(invoice.ecf_id.l10n_latam_document_type_id, ecf_informal_supplier)

    # def test_l10n_do_out_ecf_invoice_credit_fiscal_agotado(self):
    #     """"""
    #     self._setup_company_do_ecf_contingency()
    #     self.product_a.list_price = 250000.00
    #     form = self._l10n_do_create_form_move(
    #         move_type="out_invoice",
    #         internal_type="invoice",
    #         partner=self.partner_taxpayer,
    #     )
    #
    #     # with self.assertRaises(ValidationError):
    #     invoice3 = form.save()
    #     invoice3.action_post()
