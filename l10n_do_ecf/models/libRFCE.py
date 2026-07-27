# -*- coding: utf-8 -*-

from . import Mixed
from . import RFCE
from ..dgii_api import DGII_VERSION
import logging
_logger = logging.getLogger(__name__)


class libRFCE(Mixed.MixedLib):
    """Resumen Factura de Consumo Electrónica <DOP250,000 (RFCE)"""

    def gen_encabezado(self):
        classdoc = RFCE

        version = DGII_VERSION
        IdDoc = classdoc.IdDoc(TipoeCF="32",
                               eNCF=self.document_id.name,
                               TipoIngresos=self.invoice_id.l10n_do_income_type,
                               TipoPago=self.document_id.get_payment_type(),
                               )

        sender = self.gen_sender(classdoc)
        buyer = self.gen_buyer(classdoc)
        totals = self.gen_totals(classdoc)
        heading = classdoc.Encabezado(Version=version,
                                      IdDoc=IdDoc,
                                      Emisor=sender,
                                      Comprador=buyer,
                                      Totales=totals,
                                      )

        return heading

    def gen_sender(self, classdoc):
        sender = classdoc.Emisor(RNCEmisor=self.document_id.company_id.vat,
                                 RazonSocialEmisor=self.limit(self.document_id.company_id.name, 150),
                                 FechaEmision=self.invoice_id.invoice_date,
                                 )

        return sender

    def gen_buyer(self, classdoc):
        # comprador = classdoc.Comprador(RazonSocialComprador=self.limit(self.document_id.partner_id.name, 150),
        partner_id = self.document_id.partner_id
        buyer = classdoc.Comprador(RazonSocialComprador=self.limit(partner_id.name, 150))
        # if self.document_id.partner_id.vat:
        if partner_id.vat:
            # comprador.set_RNCComprador(self.document_id.partner_id.vat)
            buyer.set_RNCComprador(partner_id.vat)

        return buyer

    def gen_totals(self, classdoc):
        """Invoice amounts related values"""
        tax_data = self.document_id.get_taxed_amount_data()
        total_taxed = sum(
            [
                tax_data["18_taxed_base"],
                tax_data["16_taxed_base"],
                tax_data["0_taxed_base"],
            ]
        )
        total_itbis = sum(
            [
                tax_data["18_taxed_amount"],
                tax_data["16_taxed_amount"],
                tax_data["0_taxed_amount"],
            ]
        )

        totals = classdoc.Totales(MontoTotal=abs(round(total_taxed + total_itbis + tax_data['exempt_amount'], 2)))

        if total_taxed:
            totals.set_MontoGravadoTotal(abs(round(total_taxed, 2)))
        if tax_data["18_taxed_base"]:
            totals.set_MontoGravadoI1(abs(round(tax_data["18_taxed_base"], 2)))
        if tax_data["16_taxed_base"]:
            totals.set_MontoGravadoI2(abs(round(tax_data["16_taxed_base"], 2)))
        if tax_data["0_taxed_base"]:
            totals.set_MontoGravadoI3(abs(round(tax_data["0_taxed_base"], 2)))
        if tax_data["exempt_amount"]:
            totals.set_MontoExento(abs(round(tax_data["exempt_amount"], 2)))
        if tax_data["0_taxed_base"]:
            totals.set_TotalITBIS(0)
        if total_taxed:
            totals.set_TotalITBIS(abs(round(total_itbis, 2)))
        if tax_data["18_taxed_base"]:
            totals.set_TotalITBIS1(abs(round(tax_data["18_taxed_amount"], 2)))
        if tax_data["16_taxed_base"]:
            totals.set_TotalITBIS2(abs(round(tax_data["16_taxed_amount"], 2)))
        if tax_data["0_taxed_base"]:
            totals.set_TotalITBIS3(abs(round(tax_data["0_taxed_amount"], 2)))

        total_tax_tips = tax_data["tax_additional"]
        if total_tax_tips:
            totals.set_MontoTotal(totals.get_MontoTotal() + total_tax_tips)
            totals.set_MontoImpuestoAdicional(total_tax_tips)
        tax_additional_other = tax_data["tax_additional_other"]
        if tax_additional_other:
            totals.set_MontoTotal(totals.get_MontoTotal() + tax_additional_other)
            totals.set_MontoImpuestoAdicional(float(totals.get_MontoImpuestoAdicional() or 0.00) + tax_additional_other)

        if not total_taxed:
            totals.set_MontoTotal(abs(round(self.invoice_id.amount_untaxed, 2)))

        return totals
