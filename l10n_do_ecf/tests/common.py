# -*- coding: utf-8 -*-

from odoo import fields
from odoo.tests import tagged, Form

from odoo.addons.account.tests.common import AccountTestInvoicingCommon


@tagged('post_install_l10n', 'post_install', '-at_install')
class TestL10nDoCommon(AccountTestInvoicingCommon):

    @classmethod
    @AccountTestInvoicingCommon.setup_country('do')
    def setUpClass(cls):
        super().setUpClass()
        cls.company = cls.company_data["company"]

        # Models
        cls.Partner = cls.env["res.partner"].with_company(cls.company).sudo()
        cls.Journal = cls.env["account.journal"].with_company(cls.company)
        cls.AccountMove = cls.env["account.move"].with_company(cls.company)
        cls.current_datetime = fields.Datetime.context_timestamp(
            cls.AccountMove, fields.Datetime.now()
        )
        cls.current_date = fields.Date.context_today(cls.AccountMove)

        # Partners
        cls.partner_contact = cls.company.partner_id
        cls.partner_taxpayer = cls.Partner.create(
            {
                "name": "SOFTEJ, S.R.L",
                "country_id": cls.env.ref("base.do").id,
                "vat": "132449462",
                "email": "susivalenzuela@hotmail.com",
                "street": "SN",
            }
        )
        cls.partner_non_payer = cls.Partner.create(
            {
                "name": "Consumidor Final",
                "country_id": cls.env.ref("base.do").id,
            }
        )
        cls.partner_informal_supplier = cls.Partner.create(
            {
                "name": "Final otro",
                "vat": "12354789741",
                "country_id": cls.env.ref("base.do").id,
                "l10n_do_dgii_tax_payer_type": 'non_payer',
            }
        )

        cls.company.write(
            {
                "vat": "132347986",
                "currency_id": cls.env.ref("base.DOP").id,
                "country_id": cls.env.ref("base.do").id,
            }
        )

        # Diarios
        cls.journal_sale = cls.company_data["default_journal_sale"]
        cls.journal_purchase = cls.company_data["default_journal_purchase"]

    def _l10n_do_create_form_move(
        self,
        move_type,
        internal_type,
        partner,
        currency_id=None,
        taxes=None,
        products=None,
        journal=None,
        latam_document_type=None,
        use_payment_term=False,
        form_id=None,
        additional_context={},
    ):
        """Método base con datos genericos para crear formulario de:
         Faturas, notas de crédito,debito, liquidaciones y retenciones de venta
        :param move_type: Tipo de documento (in_invoice,out_invoice,in_refund,
          out_refund)
        :param internal_type: Tipo interno del documento(invoice,credit_note)
        :param partner: Partner del documento
        :param currency_id: Moneda
        :param number: Número del documento, si no se envia se coloca uno
        :param taxes: Impuestos, Por defecto se toma impuestos del producto
        :param products: Productos, si no se envia, se colocará un producto
        :param journal: Diario, si no se envia por defecto coloca uno
         según el internal_type y move_type; campo requerido
        :param latam_document_type: Tipo de documento, si no se envia por defecto
         coloca uno según el partner y journal; campo requerido
        :param use_payment_term: Si es True, colocará un término de pago en el
          documento, por defecto False
        :param form_id: ID del formulario si fuese diferente al de la factura,
          por defecto None
        """
        products = products or self.product_a
        move_form = Form(
            self.AccountMove.with_context(
                default_move_type=move_type,
                internal_type=internal_type,
                mail_create_nosubscribe=True,
                **additional_context
            ),
            form_id,
        )

        move_form.invoice_date = fields.Date.context_today(self.AccountMove)
        move_form.partner_id = partner
        if journal:
            move_form.journal_id = journal
        if move_form.journal_id.l10n_latam_use_documents and latam_document_type:
            move_form.l10n_latam_document_type_id = latam_document_type
        if use_payment_term:
            move_form.invoice_payment_term_id = self.env.ref(
                "account.account_payment_term_15days"
            )
        if currency_id:
            move_form.currency_id = currency_id
        for product in products or []:
            with move_form.invoice_line_ids.new() as line_form:
                line_form.product_id = product
                if taxes:
                    line_form.tax_ids.clear()
                    for tax in taxes:
                        line_form.tax_ids.add(tax)

        return move_form
