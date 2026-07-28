# -*- coding: utf-8 -*-

from .MixedClass import GeneratedsSuper
from .MixedClass import showIndent
from .MixedClass import quote_xml
import re as re_
import sys

try:
    from lxml import etree as etree_
except ImportError:
    from xml.etree import ElementTree as etree_

Validate_simpletypes_ = True
if sys.version_info.major == 2:
    BaseStrType_ = basestring
else:
    BaseStrType_ = str

try:
    from generatedsnamespaces import GenerateDSNamespaceDefs as GenerateDSNamespaceDefs_
except ImportError:
    GenerateDSNamespaceDefs_ = {}

#
# Globals
#

ExternalEncoding = 'utf-8'
Tag_pattern_ = re_.compile(r'({.*})?(.*)')
String_cleanup_pat_ = re_.compile(r"[\n\r\s]+")
Namespace_extract_pat_ = re_.compile(r'{(.*)}(.*)')
CDATA_pattern_ = re_.compile(r"<!\[CDATA\[.*?\]\]>", re_.DOTALL)

# Change this to redirect the generated superclass module to use a
# specific subclass module.
CurrentSubclassModule_ = None


#
# Data representation classes.
#


class FacturaConsumoElectronica(GeneratedsSuper):
    """Elemento Raiz de la Factura de Consumo Electrónica"""
    subclass = None
    superclass = None

    def __init__(self, Encabezado, DetallesItems=None, DescuentosORecargos=None, FechaHoraFirma=None):
        self.original_tagname_ = None
        self.Encabezado = Encabezado
        self.DetallesItems = DetallesItems
        self.DescuentosORecargos = DescuentosORecargos
        self.FechaHoraFirma = FechaHoraFirma

    def get_Encabezado(self):
        return self.Encabezado

    def set_Encabezado(self, Encabezado):
        self.Encabezado = Encabezado

    def get_DetallesItems(self):
        return self.DetallesItems

    def set_DetallesItems(self, DetallesItems):
        self.DetallesItems = DetallesItems

    def get_DescuentosORecargos(self):
        return self.DescuentosORecargos

    def set_DescuentosORecargos(self, DescuentosORecargos):
        self.DescuentosORecargos = DescuentosORecargos

    def get_FechaHoraFirma(self):
        return self.FechaHoraFirma

    def set_FechaHoraFirma(self, FechaHoraFirma):
        self.FechaHoraFirma = FechaHoraFirma

    def hasContent_(self):
        if (
                self.Encabezado is not None or
                self.DetallesItems is not None or
                self.DescuentosORecargos is not None or
                self.FechaHoraFirma is not None
        ):
            return True
        else:
            return False

    def export(self, outfile, level, namespace_='', name_='ECF', namespacedef_='', pretty_print=True):
        imported_ns_def_ = GenerateDSNamespaceDefs_.get('ECF')
        if imported_ns_def_ is not None:
            namespacedef_ = imported_ns_def_
        if pretty_print:
            eol_ = '\n'
        else:
            eol_ = ''
        if self.original_tagname_ is not None:
            name_ = self.original_tagname_
        showIndent(outfile, level, pretty_print)
        outfile.write(bytes(('<%s%s%s' % (namespace_, name_, namespacedef_ and ' ' + namespacedef_ or '',)).encode()))
        if self.hasContent_():
            outfile.write(bytes(('>%s' % (eol_,)).encode()))
            self.exportChildren(outfile, level + 1, namespace_='', name_='ECF', pretty_print=pretty_print)
            showIndent(outfile, level, pretty_print)
            outfile.write(bytes(('</%s%s>%s' % (namespace_, name_, eol_)).encode()))
        else:
            outfile.write(bytes(('/>%s' % (eol_,)).encode()))

    def exportChildren(self, outfile, level, namespace_='', name_='ECF', fromsubclass_=False,
                       pretty_print=True):
        if pretty_print:
            eol_ = '\n'
        else:
            eol_ = ''

        if self.Encabezado is not None:
            self.Encabezado.export(outfile, level, namespace_, name_='Encabezado', pretty_print=pretty_print)
        if self.DetallesItems is not None:
            self.DetallesItems.export(outfile, level, namespace_, name_='DetallesItems', pretty_print=pretty_print)
        if self.DescuentosORecargos is not None:
            self.DescuentosORecargos.export(outfile, level, namespace_, name_='DescuentosORecargos',
                                            pretty_print=pretty_print)
        if self.FechaHoraFirma is not None:
            showIndent(outfile, level, pretty_print)
            outfile.write(bytes(('<FechaHoraFirma>%s</FechaHoraFirma>%s' % (
                self.gds_encode(
                    self.gds_format_string(quote_xml(self.FechaHoraFirma), input_name='FechaHoraFirma')),
                eol_)).encode()))


class Encabezado(GeneratedsSuper):
    subclass = None
    superclass = None

    def __init__(self, Version, IdDoc, Emisor, Comprador, Totales, OtraMoneda=None):
        self.original_tagname_ = None
        self.Version = Version
        self.IdDoc = IdDoc
        self.Emisor = Emisor
        self.Comprador = Comprador
        self.Totales = Totales
        self.OtraMoneda = OtraMoneda

    def get_Version(self):
        return self.Version

    def set_Version(self, Version):
        self.Version = Version

    def get_IdDoc(self):
        return self.IdDoc

    def set_IdDoc(self, IdDoc):
        self.IdDoc = IdDoc

    def get_Emisor(self):
        return self.Emisor

    def set_Emisor(self, Emisor):
        self.Emisor = Emisor

    def get_Comprador(self):
        return self.Comprador

    def set_Comprador(self, Comprador):
        self.Comprador = Comprador

    def get_Totales(self):
        return self.Totales

    def set_Totales(self, Totales):
        self.Totales = Totales

    def get_OtraMoneda(self):
        return self.OtraMoneda

    def set_OtraMoneda(self, OtraMoneda):
        self.OtraMoneda = OtraMoneda

    def hasContent_(self):
        if (
                self.Version is not None or
                self.TipoeCF is not None or
                self.Emisor is not None or
                self.Comprador is not None or
                self.Totales is not None or
                self.OtraMoneda is not None
        ):
            return True
        else:
            return False

    def export(self, outfile, level, namespace_='', name_='Encabezado', namespacedef_='', pretty_print=True):
        imported_ns_def_ = GenerateDSNamespaceDefs_.get('Encabezado')
        if imported_ns_def_ is not None:
            namespacedef_ = imported_ns_def_
        if pretty_print:
            eol_ = '\n'
        else:
            eol_ = ''
        if self.original_tagname_ is not None:
            name_ = self.original_tagname_
        showIndent(outfile, level, pretty_print)
        outfile.write(
            bytes(('<%s%s%s' % (namespace_, name_, namespacedef_ and ' ' + namespacedef_ or '',)).encode()))
        if self.hasContent_():
            outfile.write(bytes(('>%s' % (eol_,)).encode()))
            self.exportChildren(outfile, level + 1, namespace_='', name_='Encabezado', pretty_print=pretty_print)
            showIndent(outfile, level, pretty_print)
            outfile.write(bytes(('</%s%s>%s' % (namespace_, name_, eol_)).encode()))
        else:
            outfile.write(bytes(('/>%s' % (eol_,)).encode()))

    def exportChildren(self, outfile, level, namespace_='', name_='EmisorType', fromsubclass_=False,
                       pretty_print=True):
        if pretty_print:
            eol_ = '\n'
        else:
            eol_ = ''
        if self.Version is not None:
            showIndent(outfile, level, pretty_print)
            outfile.write(bytes(('<Version>%s</Version>%s' % (
                self.gds_encode(self.gds_format_string(quote_xml(self.Version), input_name='Version')),
                eol_)).encode()))
        if self.IdDoc is not None:
            self.IdDoc.export(outfile, level, namespace_, name_='IdDoc', pretty_print=pretty_print)
        if self.Emisor is not None:
            self.Emisor.export(outfile, level, namespace_, name_='Emisor', pretty_print=pretty_print)
        if self.Comprador is not None:
            self.Comprador.export(outfile, level, namespace_, name_='Comprador', pretty_print=pretty_print)
        if self.Totales is not None:
            self.Totales.export(outfile, level, namespace_, name_='Totales', pretty_print=pretty_print)
        if self.OtraMoneda is not None:
            self.OtraMoneda.export(outfile, level, namespace_, name_='OtraMoneda', pretty_print=pretty_print)


class IdDoc(GeneratedsSuper):
    subclass = None
    superclass = None

    def __init__(self, TipoeCF, eNCF, TipoIngresos, TipoPago, IndicadorMontoGravado=None, FechaLimitePago=None,
                 TerminoPago=None, TablaFormasPago=None):
        self.original_tagname_ = None
        self.TipoeCF = TipoeCF
        self.eNCF = eNCF
        self.IndicadorMontoGravado = IndicadorMontoGravado
        self.TipoIngresos = TipoIngresos
        self.TipoPago = TipoPago
        self.FechaLimitePago = FechaLimitePago
        self.TerminoPago = TerminoPago
        self.TablaFormasPago = TablaFormasPago

    def get_TipoeCF(self):
        return self.TipoeCF

    def set_TipoeCF(self, TipoeCF):
        self.TipoeCF = TipoeCF

    def get_eNCF(self):
        return self.eNCF

    def set_eNCF(self, eNCF):
        self.eNCF = eNCF

    def get_IndicadorMontoGravado(self):
        return self.IndicadorMontoGravado

    def set_IndicadorMontoGravado(self, IndicadorMontoGravado):
        self.IndicadorMontoGravado = IndicadorMontoGravado

    def get_TipoIngresos(self):
        return self.TipoIngresos

    def set_TipoIngresos(self, TipoIngresos):
        self.TipoIngresos = TipoIngresos

    def get_TipoPago(self):
        return self.TipoPago

    def set_TipoPago(self, TipoPago):
        self.TipoPago = TipoPago

    def get_FechaLimitePago(self):
        return self.FechaLimitePago

    def set_FechaLimitePago(self, FechaLimitePago):
        self.FechaLimitePago = FechaLimitePago

    def get_TerminoPago(self):
        return self.TerminoPago

    def set_TerminoPago(self, TerminoPago):
        self.TerminoPago = TerminoPago

    def get_TablaFormasPago(self):
        return self.TablaFormasPago

    def set_TablaFormasPago(self, TablaFormasPago):
        self.TablaFormasPago = TablaFormasPago

    def hasContent_(self):
        if (
                self.TipoeCF is not None or
                self.eNCF is not None or
                self.IndicadorMontoGravado is not None or
                self.TipoIngresos is not None or
                self.TipoPago is not None or
                self.FechaLimitePago is not None or
                self.TerminoPago is not None or
                self.TablaFormasPago is not None
        ):
            return True
        else:
            return False

    def export(self, outfile, level, namespace_='', name_='IdDoc', namespacedef_='', pretty_print=True):
        imported_ns_def_ = GenerateDSNamespaceDefs_.get('IdDoc')
        if imported_ns_def_ is not None:
            namespacedef_ = imported_ns_def_
        if pretty_print:
            eol_ = '\n'
        else:
            eol_ = ''
        if self.original_tagname_ is not None:
            name_ = self.original_tagname_
        showIndent(outfile, level, pretty_print)
        outfile.write(
            bytes(('<%s%s%s' % (namespace_, name_, namespacedef_ and ' ' + namespacedef_ or '',)).encode()))
        if self.hasContent_():
            outfile.write(bytes(('>%s' % (eol_,)).encode()))
            self.exportChildren(outfile, level + 1, namespace_='', name_='IdDoc', pretty_print=pretty_print)
            showIndent(outfile, level, pretty_print)
            outfile.write(bytes(('</%s%s>%s' % (namespace_, name_, eol_)).encode()))
        else:
            outfile.write(bytes(('/>%s' % (eol_,)).encode()))

    def exportChildren(self, outfile, level, namespace_='', name_='EmisorType', fromsubclass_=False,
                       pretty_print=True):
        if pretty_print:
            eol_ = '\n'
        else:
            eol_ = ''
        if self.TipoeCF is not None:
            showIndent(outfile, level, pretty_print)
            outfile.write(bytes(('<TipoeCF>%s</TipoeCF>%s' % (
                self.gds_encode(
                    self.gds_format_string(quote_xml(self.TipoeCF), input_name='Tipo Comprobante Fiscal Electrónico')),
                eol_)).encode()))
        if self.eNCF is not None:
            showIndent(outfile, level, pretty_print)
            outfile.write(bytes(('<eNCF>%s</eNCF>%s' % (
                self.gds_encode(
                    self.gds_format_string(quote_xml(self.eNCF), input_name='eNCF')),
                eol_)).encode()))
        if self.IndicadorMontoGravado is not None:
            showIndent(outfile, level, pretty_print)
            outfile.write(bytes(('<IndicadorMontoGravado>%s</IndicadorMontoGravado>%s' % (
                self.gds_encode(
                    self.gds_format_integer(self.IndicadorMontoGravado, input_name='IndicadorMontoGravado')),
                eol_)).encode()))
        if self.TipoIngresos is not None:
            showIndent(outfile, level, pretty_print)
            outfile.write(bytes(('<TipoIngresos>%s</TipoIngresos>%s' % (
                self.gds_encode(
                    self.gds_format_string(quote_xml(self.TipoIngresos), input_name='TipoIngresos')),
                eol_)).encode()))
        if self.TipoPago is not None:
            showIndent(outfile, level, pretty_print)
            outfile.write(bytes(('<TipoPago>%s</TipoPago>%s' % (
                self.gds_encode(
                    self.gds_format_string(quote_xml(self.TipoPago), input_name='TipoPago')),
                eol_)).encode()))
        if self.FechaLimitePago is not None:
            showIndent(outfile, level, pretty_print)
            outfile.write(bytes(('<FechaLimitePago>%s</FechaLimitePago>%s' % (
                self.gds_format_date(self.FechaLimitePago, input_name='FechaLimitePago'), eol_)).encode()))
        if self.TerminoPago is not None:
            showIndent(outfile, level, pretty_print)
            outfile.write(bytes(('<TerminoPago>%s</TerminoPago>%s' % (
                self.gds_encode(
                    self.gds_format_string(quote_xml(self.TerminoPago), input_name='TerminoPago')),
                eol_)).encode()))
        if self.TablaFormasPago is not None:
            self.TablaFormasPago.export(outfile, level, namespace_, name_='TablaFormasPago', pretty_print=pretty_print)


class TablaFormasPago(GeneratedsSuper):
    subclass = None
    superclass = None

    def __init__(self, FormaDePago=None):
        self.original_tagname_ = None
        if FormaDePago is None:
            self.FormaDePago = []
        else:
            self.FormaDePago = FormaDePago

    def get_FormaDePago(self):
        return self.FormaDePago

    def set_FormaDePago(self, FormaDePago):
        self.FormaDePago = FormaDePago

    def add_FormaDePago(self, value):
        self.FormaDePago.append(value)

    def insert_FormaDePago_at(self, index, value):
        self.FormaDePago.insert(index, value)

    def replace_FormaDePago_at(self, index, value):
        self.FormaDePago[index] = value

    def hasContent_(self):
        if self.FormaDePago is not None:
            return True
        else:
            return False

    def export(self, outfile, level, namespace_='', name_='FormaDePago', namespacedef_='', pretty_print=True):
        imported_ns_def_ = GenerateDSNamespaceDefs_.get('FormaDePago')
        if imported_ns_def_ is not None:
            namespacedef_ = imported_ns_def_
        if pretty_print:
            eol_ = '\n'
        else:
            eol_ = ''
        if self.original_tagname_ is not None:
            name_ = self.original_tagname_
        showIndent(outfile, level, pretty_print)
        outfile.write(
            bytes(('<%s%s%s' % (namespace_, name_, namespacedef_ and ' ' + namespacedef_ or '',)).encode()))
        if self.hasContent_():
            outfile.write(bytes(('>%s' % (eol_,)).encode()))
            self.exportChildren(outfile, level + 1, namespace_='', name_='FormaDePago', pretty_print=pretty_print)
            showIndent(outfile, level, pretty_print)
            outfile.write(bytes(('</%s%s>%s' % (namespace_, name_, eol_)).encode()))
        else:
            outfile.write(bytes(('/>%s' % (eol_,)).encode()))

    def exportChildren(self, outfile, level, namespace_='', name_='DetalleServicioType', fromsubclass_=False,
                       pretty_print=True):
        if pretty_print:
            eol_ = '\n'
        else:
            eol_ = ''
        for LeneaMago in self.FormaDePago:
            LeneaMago.export(outfile, level, namespace_, name_='FormaDePago', pretty_print=pretty_print)


class FormaDePago(GeneratedsSuper):
    subclass = None
    superclass = None

    def __init__(self, FormaPago=None, MontoPago=None):
        self.original_tagname_ = None
        self.FormaPago = FormaPago
        self.MontoPago = MontoPago

    def get_FormaPago(self):
        return self.Version

    def set_FormaPago(self, FormaPago):
        self.FormaPago = FormaPago

    def get_MontoPago(self):
        return self.MontoPago

    def set_MontoPago(self, MontoPago):
        self.MontoPago = MontoPago

    def hasContent_(self):
        if (
                self.FormaPago is not None or
                self.MontoPago is not None
        ):
            return True
        else:
            return False

    def export(self, outfile, level, namespace_='', name_='FormaDePago', namespacedef_='', pretty_print=True):
        imported_ns_def_ = GenerateDSNamespaceDefs_.get('FormaDePago')
        if imported_ns_def_ is not None:
            namespacedef_ = imported_ns_def_
        if pretty_print:
            eol_ = '\n'
        else:
            eol_ = ''
        if self.original_tagname_ is not None:
            name_ = self.original_tagname_
        showIndent(outfile, level, pretty_print)
        outfile.write(
            bytes(('<%s%s%s' % (namespace_, name_, namespacedef_ and ' ' + namespacedef_ or '',)).encode()))
        if self.hasContent_():
            outfile.write(bytes(('>%s' % (eol_,)).encode()))
            self.exportChildren(outfile, level + 1, namespace_='', name_='FormaDePago', pretty_print=pretty_print)
            showIndent(outfile, level, pretty_print)
            outfile.write(bytes(('</%s%s>%s' % (namespace_, name_, eol_)).encode()))
        else:
            outfile.write(bytes(('/>%s' % (eol_,)).encode()))

    def exportChildren(self, outfile, level, namespace_='', name_='EmisorType', fromsubclass_=False,
                       pretty_print=True):
        if pretty_print:
            eol_ = '\n'
        else:
            eol_ = ''
        if self.FormaPago is not None:
            showIndent(outfile, level, pretty_print)
            outfile.write(bytes(('<FormaPago>%s</FormaPago>%s' % (
                self.gds_format_integer(self.FormaPago, input_name='FormaPago'), eol_)).encode()))
        if self.MontoPago is not None:
            showIndent(outfile, level, pretty_print)
            outfile.write(bytes(('<MontoPago>%s</MontoPago>%s' % (
                self.gds_encode(
                    self.gds_format_string(quote_xml(self.MontoPago), input_name='MontoPago')),
                eol_)).encode()))


class Emisor(GeneratedsSuper):
    subclass = None
    superclass = None

    def __init__(self, RNCEmisor, RazonSocialEmisor, DireccionEmisor, FechaEmision, NombreComercial=None, Sucursal=None,
                 CorreoEmisor=None, Provincia=None, Municipio=None, WebSite=None, ZonaVenta=None, CodigoVendedor=None,
                 NumeroFacturaInterna=None, NumeroPedidoInterno=None, TablaTelefonoEmisor=None,
                 InformacionAdicionalEmisor=None):
        self.original_tagname_ = None
        self.RNCEmisor = RNCEmisor
        self.RazonSocialEmisor = RazonSocialEmisor
        self.DireccionEmisor = DireccionEmisor
        self.FechaEmision = FechaEmision
        self.NombreComercial = NombreComercial
        self.Sucursal = Sucursal
        self.CorreoEmisor = CorreoEmisor
        self.Provincia = Provincia
        self.Municipio = Municipio
        self.WebSite = WebSite
        self.CodigoVendedor = CodigoVendedor
        self.NumeroFacturaInterna = NumeroFacturaInterna
        self.NumeroPedidoInterno = NumeroPedidoInterno
        self.ZonaVenta = ZonaVenta
        self.TablaTelefonoEmisor = TablaTelefonoEmisor
        self.InformacionAdicionalEmisor = InformacionAdicionalEmisor

    def get_RNCEmisor(self):
        return self.RNCEmisor

    def set_RNCEmisor(self, RNCEmisor):
        self.RNCEmisor = RNCEmisor

    def get_RazonSocialEmisor(self):
        return self.RazonSocialEmisor

    def set_RazonSocialEmisor(self, RazonSocialEmisor):
        self.RazonSocialEmisor = RazonSocialEmisor

    def get_NombreComercial(self):
        return self.NombreComercial

    def set_NombreComercial(self, NombreComercial):
        self.NombreComercial = NombreComercial

    def get_Sucursal(self):
        return self.Sucursal

    def set_Sucursal(self, Sucursal):
        self.Sucursal = Sucursal

    def get_DireccionEmisor(self):
        return self.DireccionEmisor

    def set_DireccionEmisor(self, DireccionEmisor):
        self.DireccionEmisor = DireccionEmisor

    def get_FechaEmision(self):
        return self.FechaEmision

    def set_FechaEmision(self, FechaEmision):
        self.FechaEmision = FechaEmision

    def get_CorreoEmisor(self):
        return self.CorreoEmisor

    def set_CorreoEmisor(self, CorreoEmisor):
        self.CorreoEmisor = CorreoEmisor

    def get_Provincia(self):
        return self.Provincia

    def set_Provincia(self, Provincia):
        self.Provincia = Provincia

    def get_Municipio(self):
        return self.Municipio

    def set_Municipio(self, Municipio):
        self.Municipio = Municipio

    def get_TablaTelefonoEmisor(self):
        return self.TablaTelefonoEmisor

    def set_TablaTelefonoEmisor(self, TablaTelefonoEmisor):
        self.TablaTelefonoEmisor = TablaTelefonoEmisor

    def get_WebSite(self):
        return self.WebSite

    def set_WebSite(self, WebSite):
        self.WebSite = WebSite

    def get_CodigoVendedor(self):
        return self.CodigoVendedor

    def set_CodigoVendedor(self, CodigoVendedor):
        self.CodigoVendedor = CodigoVendedor

    def get_NumeroFacturaInterna(self):
        return self.NumeroFacturaInterna

    def set_NumeroFacturaInterna(self, NumeroFacturaInterna):
        self.NumeroFacturaInterna = NumeroFacturaInterna

    def get_NumeroPedidoInterno(self):
        return self.NumeroPedidoInterno

    def set_NumeroPedidoInterno(self, NumeroPedidoInterno):
        self.NumeroPedidoInterno = NumeroPedidoInterno

    def get_ZonaVenta(self):
        return self.ZonaVenta

    def set_ZonaVenta(self, ZonaVenta):
        self.ZonaVenta = ZonaVenta

    def get_InformacionAdicionalEmisor(self):
        return self.InformacionAdicionalEmisor

    def set_InformacionAdicionalEmisor(self, InformacionAdicionalEmisor):
        self.InformacionAdicionalEmisor = InformacionAdicionalEmisor

    def hasContent_(self):
        if (
                self.RNCEmisor is not None or
                self.RazonSocialEmisor is not None or
                self.NombreComercial is not None or
                self.Sucursal is not None or
                self.DireccionEmisor is not None or
                self.FechaEmision is not None or
                self.CorreoEmisor is not None or
                self.Municipio is not None or
                self.Provincia is not None or
                self.WebSite is not None or
                self.CodigoVendedor is not None or
                self.NumeroFacturaInterna is not None or
                self.NumeroPedidoInterno is not None or
                self.ZonaVenta is not None or
                self.TablaTelefonoEmisor is not None or
                self.InformacionAdicionalEmisor is not None
        ):
            return True
        else:
            return False

    def export(self, outfile, level, namespace_='', name_='EmisorType', namespacedef_='', pretty_print=True):
        imported_ns_def_ = GenerateDSNamespaceDefs_.get('EmisorType')
        if imported_ns_def_ is not None:
            namespacedef_ = imported_ns_def_
        if pretty_print:
            eol_ = '\n'
        else:
            eol_ = ''
        if self.original_tagname_ is not None:
            name_ = self.original_tagname_
        showIndent(outfile, level, pretty_print)
        outfile.write(
            bytes(('<%s%s%s' % (namespace_, name_, namespacedef_ and ' ' + namespacedef_ or '',)).encode()))
        if self.hasContent_():
            outfile.write(bytes(('>%s' % (eol_,)).encode()))
            self.exportChildren(outfile, level + 1, namespace_='', name_='EmisorType', pretty_print=pretty_print)
            showIndent(outfile, level, pretty_print)
            outfile.write(bytes(('</%s%s>%s' % (namespace_, name_, eol_)).encode()))
        else:
            outfile.write(bytes(('/>%s' % (eol_,)).encode()))

    def exportChildren(self, outfile, level, namespace_='', name_='EmisorType', fromsubclass_=False,
                       pretty_print=True):
        if pretty_print:
            eol_ = '\n'
        else:
            eol_ = ''
        if self.RNCEmisor is not None:
            showIndent(outfile, level, pretty_print)
            outfile.write(bytes(('<RNCEmisor>%s</RNCEmisor>%s' % (
                self.gds_encode(self.gds_format_string(quote_xml(self.RNCEmisor), input_name='RNC Emisor')),
                eol_)).encode()))
        if self.RazonSocialEmisor is not None:
            showIndent(outfile, level, pretty_print)
            outfile.write(bytes(('<RazonSocialEmisor>%s</RazonSocialEmisor>%s' % (
                self.gds_encode(self.gds_format_string(quote_xml(self.RazonSocialEmisor),
                                                       input_name='Nombre o Razón Social del emisor')),
                eol_)).encode()))
        if self.NombreComercial is not None:
            showIndent(outfile, level, pretty_print)
            outfile.write(bytes(('<NombreComercial>%s</NombreComercial>%s' % (
                self.gds_encode(self.gds_format_string(quote_xml(self.NombreComercial), input_name='Nombre Comercial')),
                eol_)).encode()))
        if self.Sucursal is not None:
            showIndent(outfile, level, pretty_print)
            outfile.write(bytes(('<Sucursal>%s</Sucursal>%s' % (
                self.gds_encode(self.gds_format_string(quote_xml(self.Sucursal), input_name='Sucursal')),
                eol_)).encode()))
        if self.DireccionEmisor is not None:
            showIndent(outfile, level, pretty_print)
            outfile.write(bytes(('<DireccionEmisor>%s</DireccionEmisor>%s' % (
                self.gds_encode(
                    self.gds_format_string(quote_xml(self.DireccionEmisor), input_name='Dirección de Emisor')),
                eol_)).encode()))
        if self.Municipio is not None:
            showIndent(outfile, level, pretty_print)
            outfile.write(bytes(('<Municipio>%s</Municipio>%s' % (
                self.gds_encode(
                    self.gds_format_string(quote_xml(self.Municipio), input_name='Municipio')),
                eol_)).encode()))
        if self.Provincia is not None:
            showIndent(outfile, level, pretty_print)
            outfile.write(bytes(('<Provincia>%s</Provincia>%s' % (
                self.gds_encode(
                    self.gds_format_string(quote_xml(self.Provincia), input_name='Provincia')),
                eol_)).encode()))
        if self.TablaTelefonoEmisor is not None:
            self.TablaTelefonoEmisor.export(outfile, level, namespace_, name_='TablaTelefonoEmisor',
                                            pretty_print=pretty_print)
        if self.CorreoEmisor is not None:
            showIndent(outfile, level, pretty_print)
            outfile.write(bytes(('<CorreoEmisor>%s</CorreoEmisor>%s' % (
                self.gds_encode(
                    self.gds_format_string(quote_xml(self.CorreoEmisor), input_name='Correo Electrónico Emisor')),
                eol_)).encode()))
        if self.WebSite is not None:
            showIndent(outfile, level, pretty_print)
            outfile.write(bytes(('<WebSite>%s</WebSite>%s' % (
                self.gds_encode(
                    self.gds_format_string(quote_xml(self.WebSite), input_name='WebSite')),
                eol_)).encode()))
        if self.CodigoVendedor is not None:
            showIndent(outfile, level, pretty_print)
            outfile.write(bytes(('<CodigoVendedor>%s</CodigoVendedor>%s' % (
                self.gds_encode(
                    self.gds_format_string(quote_xml(self.CodigoVendedor), input_name='Código del Vendedor')),
                eol_)).encode()))
        if self.NumeroFacturaInterna is not None:
            showIndent(outfile, level, pretty_print)
            outfile.write(bytes(('<NumeroFacturaInterna>%s</NumeroFacturaInterna>%s' % (
                self.gds_encode(
                    self.gds_format_string(quote_xml(self.NumeroFacturaInterna), input_name='NumeroFacturaInterna')),
                eol_)).encode()))
        if self.NumeroPedidoInterno is not None:
            showIndent(outfile, level, pretty_print)
            outfile.write(bytes(('<NumeroPedidoInterno>%s</NumeroPedidoInterno>%s' % (
                self.gds_encode(
                    self.gds_format_string(quote_xml(self.NumeroPedidoInterno),
                                           input_name='NumeroPedidoInterno')),
                eol_)).encode()))
        if self.ZonaVenta is not None:
            showIndent(outfile, level, pretty_print)
            outfile.write(bytes(('<ZonaVenta>%s</ZonaVenta>%s' % (
                self.gds_encode(
                    self.gds_format_string(quote_xml(self.ZonaVenta), input_name='Zona de Venta')),
                eol_)).encode()))
        if self.InformacionAdicionalEmisor is not None:
            showIndent(outfile, level, pretty_print)
            outfile.write(bytes(('<InformacionAdicionalEmisor>%s</InformacionAdicionalEmisor>%s' % (
                self.gds_encode(
                    self.gds_format_string(quote_xml(self.InformacionAdicionalEmisor),
                                           input_name='Información adicional Emisor')),
                eol_)).encode()))
        if self.FechaEmision is not None:
            showIndent(outfile, level, pretty_print)
            outfile.write(bytes(('<FechaEmision>%s</FechaEmision>%s' % (
                self.gds_format_date(self.FechaEmision, input_name='FechaEmision'), eol_)).encode()))


class TablaTelefonoEmisor(GeneratedsSuper):
    subclass = None
    superclass = None

    def __init__(self, TelefonoEmisor=None):
        self.original_tagname_ = None
        if TelefonoEmisor is None:
            self.TelefonoEmisor = []
        else:
            self.TelefonoEmisor = TelefonoEmisor

    def get_TelefonoEmisor(self):
        return self.TelefonoEmisor

    def set_TelefonoEmisor(self, TelefonoEmisor):
        self.TelefonoEmisor = TelefonoEmisor

    def add_TelefonoEmisor(self, value):
        self.TelefonoEmisor.append(value)

    def insert_TelefonoEmisor_at(self, index, value):
        self.TelefonoEmisor.insert(index, value)

    def replace_FormaDePago_at(self, index, value):
        self.TelefonoEmisor[index] = value

    def hasContent_(self):
        if self.TelefonoEmisor is not None:
            return True
        else:
            return False

    def export(self, outfile, level, namespace_='', name_='TablaTelefonoEmisor', namespacedef_='', pretty_print=True):
        imported_ns_def_ = GenerateDSNamespaceDefs_.get('FormaDePago')
        if imported_ns_def_ is not None:
            namespacedef_ = imported_ns_def_
        if pretty_print:
            eol_ = '\n'
        else:
            eol_ = ''
        if self.original_tagname_ is not None:
            name_ = self.original_tagname_
        showIndent(outfile, level, pretty_print)
        outfile.write(
            bytes(('<%s%s%s' % (namespace_, name_, namespacedef_ and ' ' + namespacedef_ or '',)).encode()))
        if self.hasContent_():
            outfile.write(bytes(('>%s' % (eol_,)).encode()))
            self.exportChildren(outfile, level + 1, namespace_='', name_='TablaTelefonoEmisor',
                                pretty_print=pretty_print)
            showIndent(outfile, level, pretty_print)
            outfile.write(bytes(('</%s%s>%s' % (namespace_, name_, eol_)).encode()))
        else:
            outfile.write(bytes(('/>%s' % (eol_,)).encode()))

    def exportChildren(self, outfile, level, namespace_='', name_='DetalleServicioType', fromsubclass_=False,
                       pretty_print=True):
        if pretty_print:
            eol_ = '\n'
        else:
            eol_ = ''
        for Tel in self.TelefonoEmisor:
            showIndent(outfile, level, pretty_print)
            outfile.write(bytes(('<TelefonoEmisor>%s</TelefonoEmisor>%s' % (
                self.gds_encode(
                    self.gds_format_string(quote_xml(Tel), input_name='TelefonoEmisor')),
                eol_)).encode()))


class Comprador(GeneratedsSuper):
    subclass = None
    superclass = None

    def __init__(self, RazonSocialComprador=None, RNCComprador=None, ContactoComprador=None, CorreoComprador=None,
                 DireccionComprador=None, MunicipioComprador=None, ProvinciaComprador=None, FechaEntrega=None,
                 FechaOrdenCompra=None, NumeroOrdenCompra=None, IdentificadorExtranjero=None,
                 CodigoInternoComprador=None):
        self.original_tagname_ = None
        self.RNCComprador = RNCComprador
        self.IdentificadorExtranjero = IdentificadorExtranjero
        self.RazonSocialComprador = RazonSocialComprador
        self.ContactoComprador = ContactoComprador
        self.CorreoComprador = CorreoComprador
        self.DireccionComprador = DireccionComprador
        self.MunicipioComprador = MunicipioComprador
        self.ProvinciaComprador = ProvinciaComprador
        self.FechaEntrega = FechaEntrega
        self.FechaOrdenCompra = FechaOrdenCompra
        self.NumeroOrdenCompra = NumeroOrdenCompra
        self.CodigoInternoComprador = CodigoInternoComprador

    def get_RNCComprador(self):
        return self.RNCComprador

    def set_RNCComprador(self, RNCComprador):
        self.RNCComprador = RNCComprador

    def get_IdentificadorExtranjero(self):
        return self.IdentificadorExtranjero

    def set_IdentificadorExtranjero(self, IdentificadorExtranjero):
        self.IdentificadorExtranjero = IdentificadorExtranjero

    def get_RazonSocialComprador(self):
        return self.RazonSocialComprador

    def set_RazonSocialComprador(self, RazonSocialComprador):
        self.RazonSocialComprador = RazonSocialComprador

    def get_ContactoComprador(self):
        return self.ContactoComprador

    def set_ContactoComprador(self, ContactoComprador):
        self.ContactoComprador = ContactoComprador

    def get_CorreoComprador(self):
        return self.CorreoComprador

    def set_CorreoComprador(self, CorreoComprador):
        self.CorreoComprador = CorreoComprador

    def get_DireccionComprador(self):
        return self.DireccionComprador

    def set_DireccionComprador(self, DireccionComprador):
        self.DireccionComprador = DireccionComprador

    def get_MunicipioComprador(self):
        return self.MunicipioComprador

    def set_MunicipioComprador(self, MunicipioComprador):
        self.MunicipioComprador = MunicipioComprador

    def get_ProvinciaComprador(self):
        return self.ProvinciaComprador

    def set_ProvinciaComprador(self, ProvinciaComprador):
        self.ProvinciaComprador = ProvinciaComprador

    def get_FechaEntrega(self):
        return self.FechaEntrega

    def set_FechaEntrega(self, FechaEntrega):
        self.FechaEntrega = FechaEntrega

    def get_FechaOrdenCompra(self):
        return self.FechaOrdenCompra

    def set_FechaOrdenCompra(self, FechaOrdenCompra):
        self.FechaOrdenCompra = FechaOrdenCompra

    def get_NumeroOrdenCompra(self):
        return self.NumeroOrdenCompra

    def set_NumeroOrdenCompra(self, NumeroOrdenCompra):
        self.NumeroOrdenCompra = NumeroOrdenCompra

    def get_CodigoInternoComprador(self):
        return self.CodigoInternoComprador

    def set_CodigoInternoComprador(self, CodigoInternoComprador):
        self.CodigoInternoComprador = CodigoInternoComprador

    def hasContent_(self):
        if (
                self.RNCComprador is not None or
                self.IdentificadorExtranjero is not None or
                self.RazonSocialComprador is not None or
                self.ContactoComprador is not None or
                self.CorreoComprador is not None or
                self.DireccionComprador is not None or
                self.MunicipioComprador is not None or
                self.ProvinciaComprador is not None or
                self.FechaEntrega is not None or
                self.FechaOrdenCompra is not None or
                self.NumeroOrdenCompra is not None or
                self.CodigoInternoComprador is not None
        ):
            return True
        else:
            return False

    def export(self, outfile, level, namespace_='', name_='CompradorType', namespacedef_='', pretty_print=True):
        imported_ns_def_ = GenerateDSNamespaceDefs_.get('CompradorType')
        if imported_ns_def_ is not None:
            namespacedef_ = imported_ns_def_
        if pretty_print:
            eol_ = '\n'
        else:
            eol_ = ''
        if self.original_tagname_ is not None:
            name_ = self.original_tagname_
        showIndent(outfile, level, pretty_print)
        outfile.write(bytes(('<%s%s%s' % (namespace_, name_, namespacedef_ and ' ' + namespacedef_ or '',)).encode()))
        if self.hasContent_():
            outfile.write(bytes(('>%s' % (eol_,)).encode()))
            self.exportChildren(outfile, level + 1, namespace_='', name_='CompradorType', pretty_print=pretty_print)
            showIndent(outfile, level, pretty_print)
            outfile.write(bytes(('</%s%s>%s' % (namespace_, name_, eol_)).encode()))
        else:
            outfile.write(bytes(('/>%s' % (eol_,)).encode()))

    def exportChildren(self, outfile, level, namespace_='', name_='ReceptorType', fromsubclass_=False,
                       pretty_print=True):
        if pretty_print:
            eol_ = '\n'
        else:
            eol_ = ''
        if self.RNCComprador is not None:
            showIndent(outfile, level, pretty_print)
            outfile.write(bytes(('<RNCComprador>%s</RNCComprador>%s' % (
                self.gds_encode(self.gds_format_string(quote_xml(self.RNCComprador), input_name='RNC Comprador')),
                eol_)).encode()))
        if self.IdentificadorExtranjero is not None:
            showIndent(outfile, level, pretty_print)
            outfile.write(bytes(('<IdentificadorExtranjero>%s</IdentificadorExtranjero>%s' % (
                self.gds_encode(self.gds_format_string(quote_xml(self.IdentificadorExtranjero),
                                                       input_name='Identificador Extranjero')),
                eol_)).encode()))
        if self.RazonSocialComprador is not None:
            showIndent(outfile, level, pretty_print)
            outfile.write(bytes(('<RazonSocialComprador>%s</RazonSocialComprador>%s' % (
                self.gds_encode(self.gds_format_string(quote_xml(self.RazonSocialComprador),
                                                       input_name='Nombre o Razón Social Comprador')), eol_)).encode()))
        if self.ContactoComprador is not None:
            showIndent(outfile, level, pretty_print)
            outfile.write(bytes(('<ContactoComprador>%s</ContactoComprador>%s' % (
                self.gds_encode(
                    self.gds_format_string(quote_xml(self.ContactoComprador), input_name='Contacto Comprador')),
                eol_)).encode()))
        if self.CorreoComprador is not None:
            showIndent(outfile, level, pretty_print)
            outfile.write(bytes(('<CorreoComprador>%s</CorreoComprador>%s' % (
                self.gds_encode(self.gds_format_string(quote_xml(self.CorreoComprador), input_name='Correo Comprador')),
                eol_)).encode()))
        if self.DireccionComprador is not None:
            showIndent(outfile, level, pretty_print)
            outfile.write(bytes(('<DireccionComprador>%s</DireccionComprador>%s' % (
                self.gds_encode(
                    self.gds_format_string(quote_xml(self.DireccionComprador), input_name='Contacto Comprador')),
                eol_)).encode()))
        if self.MunicipioComprador is not None:
            showIndent(outfile, level, pretty_print)
            outfile.write(bytes(('<MunicipioComprador>%s</MunicipioComprador>%s' % (
                self.gds_encode(
                    self.gds_format_string(quote_xml(self.MunicipioComprador), input_name='Municipio Comprador')),
                eol_)).encode()))
        if self.ProvinciaComprador is not None:
            showIndent(outfile, level, pretty_print)
            outfile.write(bytes(('<ProvinciaComprador>%s</ProvinciaComprador>%s' % (
                self.gds_encode(
                    self.gds_format_string(quote_xml(self.ProvinciaComprador), input_name='Provincia Comprador')),
                eol_)).encode()))
        if self.FechaEntrega is not None:
            showIndent(outfile, level, pretty_print)
            outfile.write(bytes(('<FechaEntrega>%s</FechaEntrega>%s' % (
                self.gds_format_date(self.FechaEntrega, input_name='FechaEntrega'), eol_)).encode()))
        if self.FechaOrdenCompra is not None:
            showIndent(outfile, level, pretty_print)
            outfile.write(bytes(('<FechaOrdenCompra>%s</FechaOrdenCompra>%s' % (
                self.gds_format_date(self.FechaOrdenCompra, input_name='Fecha Orden de Compra'), eol_)).encode()))
        if self.NumeroOrdenCompra is not None:
            showIndent(outfile, level, pretty_print)
            outfile.write(bytes(('<NumeroOrdenCompra>%s</NumeroOrdenCompra>%s' % (
                self.gds_encode(
                    self.gds_format_string(quote_xml(self.NumeroOrdenCompra), input_name='Número de Orden de Compra')),
                eol_)).encode()))
        if self.CodigoInternoComprador is not None:
            showIndent(outfile, level, pretty_print)
            outfile.write(bytes(('<CodigoInternoComprador>%s</CodigoInternoComprador>%s' % (
                self.gds_encode(
                    self.gds_format_string(quote_xml(self.CodigoInternoComprador),
                                           input_name='CodigoInternoComprador')),
                eol_)).encode()))


class Totales(GeneratedsSuper):
    subclass = None
    superclass = None

    def __init__(self, MontoTotal, MontoGravadoTotal=0.00, MontoGravadoI1=0.00, MontoGravadoI2=0.00,
                 MontoGravadoI3=0.00, MontoExento=0.00, ITBIS1=0.00, ITBIS2=0.00, ITBIS3=0.00, TotalITBIS=0.00,
                 TotalITBIS1=0.00, TotalITBIS2=0.00, TotalITBIS3=0.00, ValorPagar=None, MontoImpuestoAdicional=None,
                 ImpuestosAdicionales=None):
        self.original_tagname_ = None

        self.MontoGravadoTotal = MontoGravadoTotal
        self.MontoGravadoI1 = MontoGravadoI1
        self.MontoGravadoI2 = MontoGravadoI2
        self.MontoGravadoI3 = MontoGravadoI3
        self.MontoExento = MontoExento
        self.ITBIS1 = ITBIS1
        self.ITBIS2 = ITBIS2
        self.ITBIS3 = ITBIS3
        self.TotalITBIS2 = TotalITBIS2
        self.TotalITBIS3 = TotalITBIS3
        self.TotalITBIS = TotalITBIS
        self.TotalITBIS1 = TotalITBIS1
        self.MontoTotal = MontoTotal
        self.ValorPagar = ValorPagar
        self.MontoImpuestoAdicional = MontoImpuestoAdicional
        self.ImpuestosAdicionales = ImpuestosAdicionales

    def get_MontoGravadoTotal(self):
        return self.MontoGravadoTotal

    def set_MontoGravadoTotal(self, MontoGravadoTotal):
        self.MontoGravadoTotal = MontoGravadoTotal

    def get_MontoGravadoI1(self):
        return self.MontoGravadoI1

    def set_MontoGravadoI1(self, MontoGravadoI1):
        self.MontoGravadoI1 = MontoGravadoI1

    def get_MontoGravadoI2(self):
        return self.MontoGravadoI2

    def set_MontoGravadoI2(self, MontoGravadoI2):
        self.MontoGravadoI2 = MontoGravadoI2

    def get_MontoGravadoI3(self):
        return self.MontoGravadoI3

    def set_MontoGravadoI3(self, MontoGravadoI3):
        self.MontoGravadoI3 = MontoGravadoI3

    def get_MontoExento(self):
        return self.MontoExento

    def set_MontoExento(self, MontoExento):
        self.MontoExento = MontoExento

    def get_ITBIS1(self):
        return self.ITBIS1

    def set_ITBIS1(self, ITBIS1):
        self.ITBIS1 = ITBIS1

    def get_ITBIS2(self):
        return self.ITBIS2

    def set_ITBIS2(self, ITBIS2):
        self.ITBIS2 = ITBIS2

    def get_ITBIS3(self):
        return self.ITBIS3

    def set_ITBIS3(self, ITBIS3):
        self.ITBIS3 = ITBIS3

    def get_TotalITBIS(self):
        return self.TotalITBIS

    def set_TotalITBIS(self, TotalITBIS):
        self.TotalITBIS = TotalITBIS

    def get_TotalITBIS1(self):
        return self.TotalITBIS1

    def set_TotalITBIS1(self, TotalITBIS1):
        self.TotalITBIS1 = TotalITBIS1

    def get_TotalITBIS2(self):
        return self.TotalITBIS2

    def set_TotalITBIS2(self, TotalITBIS2):
        self.TotalITBIS2 = TotalITBIS2

    def get_TotalITBIS3(self):
        return self.TotalITBIS3

    def set_TotalITBIS3(self, TotalITBIS3):
        self.TotalITBIS3 = TotalITBIS3

    def get_MontoTotal(self):
        return self.MontoTotal

    def set_MontoTotal(self, MontoTotal):
        self.MontoTotal = MontoTotal

    def get_ValorPagar(self):
        return self.ValorPagar

    def set_ValorPagar(self, ValorPagar):
        self.ValorPagar = ValorPagar

    def get_MontoImpuestoAdicional(self):
        return self.MontoImpuestoAdicional

    def set_MontoImpuestoAdicional(self, MontoImpuestoAdicional):
        self.MontoImpuestoAdicional = MontoImpuestoAdicional

    def get_ImpuestosAdicionales(self):
        return self.ImpuestosAdicionales

    def set_ImpuestosAdicionales(self, ImpuestosAdicionales):
        self.ImpuestosAdicionales = ImpuestosAdicionales

    def hasContent_(self):
        if (
                self.MontoGravadoTotal is not None or
                self.MontoGravadoI1 is not None or
                self.MontoGravadoI2 is not None or
                self.MontoGravadoI3 is not None or
                self.MontoExento is not None or
                self.ITBIS1 is not None or
                self.ITBIS2 is not None or
                self.ITBIS3 is not None or
                self.TotalITBIS is not None or
                self.TotalITBIS1 is not None or
                self.TotalITBIS2 is not None or
                self.TotalITBIS3 is not None or
                self.MontoTotal is not None or
                self.ValorPagar is not None or
                self.MontoImpuestoAdicional is not None or
                self.ImpuestosAdicionales is not None
        ):
            return True
        else:
            return False

    def export(self, outfile, level, namespace_='', name_='Totales', namespacedef_='', pretty_print=True):
        imported_ns_def_ = GenerateDSNamespaceDefs_.get('Totales')
        if imported_ns_def_ is not None:
            namespacedef_ = imported_ns_def_
        if pretty_print:
            eol_ = '\n'
        else:
            eol_ = ''
        if self.original_tagname_ is not None:
            name_ = self.original_tagname_
        showIndent(outfile, level, pretty_print)
        outfile.write(bytes(('<%s%s%s' % (namespace_, name_, namespacedef_ and ' ' + namespacedef_ or '',)).encode()))
        if self.hasContent_():
            outfile.write(bytes(('>%s' % (eol_,)).encode()))
            self.exportChildren(outfile, level + 1, namespace_='', name_='Totales', pretty_print=pretty_print)
            showIndent(outfile, level, pretty_print)
            outfile.write(bytes(('</%s%s>%s' % (namespace_, name_, eol_)).encode()))
        else:
            outfile.write(bytes(('/>%s' % (eol_,)).encode()))

    def exportChildren(self, outfile, level, namespace_='', name_='ReceptorType', fromsubclass_=False,
                       pretty_print=True):
        if pretty_print:
            eol_ = '\n'
        else:
            eol_ = ''

        if self.MontoGravadoTotal is not None:
            showIndent(outfile, level, pretty_print)
            outfile.write(bytes(('<MontoGravadoTotal>%s</MontoGravadoTotal>%s' % (
                self.gds_format_float(self.MontoGravadoTotal, input_name='Monto Gravado Total'), eol_)).encode()))
        if self.MontoGravadoI1 is not None:
            showIndent(outfile, level, pretty_print)
            outfile.write(bytes(('<MontoGravadoI1>%s</MontoGravadoI1>%s' % (
                self.gds_format_float(self.MontoGravadoI1, input_name='Monto Gravado ITBIS Tasa 1'), eol_)).encode()))
        if self.MontoGravadoI2 is not None:
            showIndent(outfile, level, pretty_print)
            outfile.write(bytes(('<MontoGravadoI2>%s</MontoGravadoI2>%s' % (
                self.gds_format_float(self.MontoGravadoI2, input_name='Monto Gravado ITBIS Tasa 2'), eol_)).encode()))
        if self.MontoGravadoI3 is not None:
            showIndent(outfile, level, pretty_print)
            outfile.write(bytes(('<MontoGravadoI3>%s</MontoGravadoI3>%s' % (
                self.gds_format_float(self.MontoGravadoI3, input_name='Monto Gravado ITBIS Tasa 3'), eol_)).encode()))
        if self.MontoExento is not None:
            showIndent(outfile, level, pretty_print)
            outfile.write(bytes(('<MontoExento>%s</MontoExento>%s' % (
                self.gds_format_float(self.MontoExento, input_name='Monto Exento'), eol_)).encode()))
        if self.ITBIS1 is not None:
            showIndent(outfile, level, pretty_print)
            outfile.write(bytes(('<ITBIS1>%s</ITBIS1>%s' % (
                self.gds_format_integer(self.ITBIS1, input_name='ITBIS Tasa 1'), eol_)).encode()))
        if self.ITBIS2 is not None:
            showIndent(outfile, level, pretty_print)
            outfile.write(bytes(('<ITBIS2>%s</ITBIS2>%s' % (
                self.gds_format_integer(self.ITBIS2, input_name='ITBIS Tasa 2'), eol_)).encode()))
        if self.ITBIS3 is not None:
            showIndent(outfile, level, pretty_print)
            outfile.write(bytes(('<ITBIS3>%s</ITBIS3>%s' % (
                self.gds_format_integer(self.ITBIS3, input_name='ITBIS Tasa 3'), eol_)).encode()))
        if self.TotalITBIS is not None:
            showIndent(outfile, level, pretty_print)
            outfile.write(bytes(('<TotalITBIS>%s</TotalITBIS>%s' % (
                self.gds_format_float(self.TotalITBIS, input_name='Total ITBIS'), eol_)).encode()))
        if self.TotalITBIS1 is not None:
            showIndent(outfile, level, pretty_print)
            outfile.write(bytes(('<TotalITBIS1>%s</TotalITBIS1>%s' % (
                self.gds_format_float(self.TotalITBIS1, input_name='Total ITBIS Tasa 1'), eol_)).encode()))
        if self.TotalITBIS2 is not None:
            showIndent(outfile, level, pretty_print)
            outfile.write(bytes(('<TotalITBIS2>%s</TotalITBIS2>%s' % (
                self.gds_format_float(self.TotalITBIS2, input_name='Total ITBIS Tasa 2'), eol_)).encode()))
        if self.TotalITBIS3 is not None:
            showIndent(outfile, level, pretty_print)
            outfile.write(bytes(('<TotalITBIS3>%s</TotalITBIS3>%s' % (
                self.gds_format_float(self.TotalITBIS3, input_name='Total ITBIS Tasa 3'), eol_)).encode()))
        if self.MontoImpuestoAdicional is not None:
            showIndent(outfile, level, pretty_print)
            outfile.write(bytes(('<MontoImpuestoAdicional>%s</MontoImpuestoAdicional>%s' % (
                self.gds_format_float(self.MontoImpuestoAdicional, input_name='MontoImpuestoAdicional'),
                eol_)).encode()))
        if self.ImpuestosAdicionales is not None:
            self.ImpuestosAdicionales.export(outfile, level, namespace_, name_='ImpuestosAdicionales',
                                             pretty_print=pretty_print)
        if self.MontoTotal is not None:
            showIndent(outfile, level, pretty_print)
            outfile.write(bytes(('<MontoTotal>%s</MontoTotal>%s' % (
                self.gds_format_float(self.MontoTotal, input_name='Monto Total'), eol_)).encode()))
        if self.ValorPagar is not None:
            showIndent(outfile, level, pretty_print)
            outfile.write(bytes(('<ValorPagar>%s</ValorPagar>%s' % (
                self.gds_format_float(self.ValorPagar, input_name='ValorPagar'), eol_)).encode()))


class OtraMoneda(GeneratedsSuper):
    subclass = None
    superclass = None

    def __init__(self, TipoMoneda=None, TipoCambio=None, MontoGravadoTotalOtraMoneda=0.00, MontoGravado1OtraMoneda=0.00,
                 MontoGravado2OtraMoneda=0.00, MontoGravado3OtraMoneda=0.00, MontoExentoOtraMoneda=0.00,
                 TotalITBISOtraMoneda=0.00, TotalITBIS1OtraMoneda=0.00, TotalITBIS2OtraMoneda=0.00,
                 TotalITBIS3OtraMoneda=0.00, MontoImpuestoAdicionalOtraMoneda=None, ImpuestosAdicionalesOtraMoneda=None,
                 MontoTotalOtraMoneda=None):
        self.original_tagname_ = None
        self.TipoMoneda = TipoMoneda
        self.TipoCambio = TipoCambio
        self.MontoGravadoTotalOtraMoneda = MontoGravadoTotalOtraMoneda
        self.MontoGravado1OtraMoneda = MontoGravado1OtraMoneda
        self.MontoGravado2OtraMoneda = MontoGravado2OtraMoneda
        self.MontoGravado3OtraMoneda = MontoGravado3OtraMoneda
        self.MontoExentoOtraMoneda = MontoExentoOtraMoneda
        self.TotalITBISOtraMoneda = TotalITBISOtraMoneda
        self.TotalITBIS1OtraMoneda = TotalITBIS1OtraMoneda
        self.TotalITBIS2OtraMoneda = TotalITBIS2OtraMoneda
        self.TotalITBIS3OtraMoneda = TotalITBIS3OtraMoneda
        self.MontoImpuestoAdicionalOtraMoneda = MontoImpuestoAdicionalOtraMoneda
        self.ImpuestosAdicionalesOtraMoneda = ImpuestosAdicionalesOtraMoneda
        self.MontoTotalOtraMoneda = MontoTotalOtraMoneda

    def get_TipoMoneda(self):
        return self.TipoMoneda

    def set_TipoMoneda(self, TipoMoneda):
        self.TipoMoneda = TipoMoneda

    def get_TipoCambio(self):
        return self.TipoCambio

    def set_TipoCambio(self, TipoCambio):
        self.TipoCambio = TipoCambio

    def get_MontoGravadoTotalOtraMoneda(self):
        return self.MontoGravadoTotalOtraMoneda

    def set_MontoGravadoTotalOtraMoneda(self, MontoGravadoTotalOtraMoneda):
        self.MontoGravadoTotalOtraMoneda = MontoGravadoTotalOtraMoneda

    def get_MontoGravado1OtraMoneda(self):
        return self.MontoGravado1OtraMoneda

    def set_MontoGravado1OtraMoneda(self, MontoGravado1OtraMoneda):
        self.MontoGravado1OtraMoneda = MontoGravado1OtraMoneda

    def get_MontoGravado2OtraMoneda(self):
        return self.MontoGravado2OtraMoneda

    def set_MontoGravado2OtraMoneda(self, MontoGravado2OtraMoneda):
        self.MontoGravado2OtraMoneda = MontoGravado2OtraMoneda

    def get_MontoGravado3OtraMoneda(self):
        return self.MontoGravado3OtraMoneda

    def set_MontoGravado3OtraMoneda(self, MontoGravado3OtraMoneda):
        self.MontoGravado3OtraMoneda = MontoGravado3OtraMoneda

    def get_MontoExentoOtraMoneda(self):
        return self.MontoExentoOtraMoneda

    def set_MontoExentoOtraMoneda(self, MontoExentoOtraMoneda):
        self.MontoExentoOtraMoneda = MontoExentoOtraMoneda

    def get_TotalITBISOtraMoneda(self):
        return self.TotalITBISOtraMoneda

    def set_TotalITBISOtraMoneda(self, TotalITBISOtraMoneda):
        self.TotalITBISOtraMoneda = TotalITBISOtraMoneda

    def get_TotalITBIS1OtraMoneda(self):
        return self.TotalITBIS1OtraMoneda

    def set_TotalITBIS1OtraMoneda(self, TotalITBIS1OtraMoneda):
        self.TotalITBIS1OtraMoneda = TotalITBIS1OtraMoneda

    def get_TotalITBIS2OtraMoneda(self):
        return self.TotalITBIS2OtraMoneda

    def set_TotalITBIS2OtraMoneda(self, TotalITBIS2OtraMoneda):
        self.TotalITBIS2OtraMoneda = TotalITBIS2OtraMoneda

    def get_TotalITBIS3OtraMoneda(self):
        return self.TotalITBIS3OtraMoneda

    def set_TotalITBIS3OtraMoneda(self, TotalITBIS3OtraMoneda):
        self.TotalITBIS3OtraMoneda = TotalITBIS3OtraMoneda

    def get_MontoImpuestoAdicionalOtraMoneda(self):
        return self.MontoImpuestoAdicionalOtraMoneda

    def set_MontoImpuestoAdicionalOtraMoneda(self, MontoImpuestoAdicionalOtraMoneda):
        self.MontoImpuestoAdicionalOtraMoneda = MontoImpuestoAdicionalOtraMoneda

    def get_ImpuestosAdicionalesOtraMoneda(self):
        return self.ImpuestosAdicionalesOtraMoneda

    def set_ImpuestosAdicionalesOtraMoneda(self, ImpuestosAdicionalesOtraMoneda):
        self.ImpuestosAdicionalesOtraMoneda = ImpuestosAdicionalesOtraMoneda

    def get_MontoTotalOtraMoneda(self):
        return self.MontoTotalOtraMoneda

    def set_MontoTotalOtraMoneda(self, MontoTotalOtraMoneda):
        self.MontoTotalOtraMoneda = MontoTotalOtraMoneda

    def hasContent_(self):
        if (
                self.TipoMoneda is not None or
                self.TipoCambio is not None or
                self.MontoGravadoTotalOtraMoneda is not None or
                self.MontoGravado1OtraMoneda is not None or
                self.MontoGravado2OtraMoneda is not None or
                self.MontoGravado3OtraMoneda is not None or
                self.MontoExentoOtraMoneda is not None or
                self.TotalITBISOtraMoneda is not None or
                self.TotalITBIS1OtraMoneda is not None or
                self.TotalITBIS2OtraMoneda is not None or
                self.TotalITBIS3OtraMoneda is not None or
                self.MontoImpuestoAdicionalOtraMoneda is not None or
                self.ImpuestosAdicionalesOtraMoneda is not None or
                self.MontoTotalOtraMoneda is not None
        ):
            return True
        else:
            return False

    def export(self, outfile, level, namespace_='', name_='OtraMoneda', namespacedef_='', pretty_print=True):
        imported_ns_def_ = GenerateDSNamespaceDefs_.get('OtraMoneda')
        if imported_ns_def_ is not None:
            namespacedef_ = imported_ns_def_
        if pretty_print:
            eol_ = '\n'
        else:
            eol_ = ''
        if self.original_tagname_ is not None:
            name_ = self.original_tagname_
        showIndent(outfile, level, pretty_print)
        outfile.write(bytes(('<%s%s%s' % (namespace_, name_, namespacedef_ and ' ' + namespacedef_ or '',)).encode()))
        if self.hasContent_():
            outfile.write(bytes(('>%s' % (eol_,)).encode()))
            self.exportChildren(outfile, level + 1, namespace_='', name_='OtraMoneda', pretty_print=pretty_print)
            showIndent(outfile, level, pretty_print)
            outfile.write(bytes(('</%s%s>%s' % (namespace_, name_, eol_)).encode()))
        else:
            outfile.write(bytes(('/>%s' % (eol_,)).encode()))

    def exportChildren(self, outfile, level, namespace_='', name_='ReceptorType', fromsubclass_=False,
                       pretty_print=True):
        if pretty_print:
            eol_ = '\n'
        else:
            eol_ = ''

        if self.TipoMoneda is not None:
            showIndent(outfile, level, pretty_print)
            outfile.write(bytes(('<TipoMoneda>%s</TipoMoneda>%s' % (
                self.gds_encode(
                    self.gds_format_string(quote_xml(self.TipoMoneda), input_name='TipoMoneda')),
                eol_)).encode()))
        if self.TipoCambio is not None:
            showIndent(outfile, level, pretty_print)
            outfile.write(bytes(('<TipoCambio>%s</TipoCambio>%s' % (
                self.gds_format_float(self.TipoCambio, input_name='TipoCambio', digits=4), eol_)).encode()))
        if self.MontoGravadoTotalOtraMoneda is not None:
            showIndent(outfile, level, pretty_print)
            outfile.write(bytes(('<MontoGravadoTotalOtraMoneda>%s</MontoGravadoTotalOtraMoneda>%s' % (
                self.gds_format_float(self.MontoGravadoTotalOtraMoneda, input_name='MontoGravadoTotalOtraMoneda'),
                eol_)).encode()))
        if self.MontoGravado1OtraMoneda is not None:
            showIndent(outfile, level, pretty_print)
            outfile.write(bytes(('<MontoGravado1OtraMoneda>%s</MontoGravado1OtraMoneda>%s' % (
                self.gds_format_float(self.MontoGravado1OtraMoneda, input_name='MontoGravado1OtraMoneda'),
                eol_)).encode()))
        if self.MontoGravado2OtraMoneda is not None:
            showIndent(outfile, level, pretty_print)
            outfile.write(bytes(('<MontoGravado2OtraMoneda>%s</MontoGravado2OtraMoneda>%s' % (
                self.gds_format_float(self.MontoGravado2OtraMoneda, input_name='MontoGravado2OtraMoneda'),
                eol_)).encode()))
        if self.MontoGravado3OtraMoneda is not None:
            showIndent(outfile, level, pretty_print)
            outfile.write(bytes(('<MontoGravado3OtraMoneda>%s</MontoGravado3OtraMoneda>%s' % (
                self.gds_format_float(self.MontoGravado3OtraMoneda, input_name='MontoGravado3OtraMoneda'),
                eol_)).encode()))
        if self.MontoExentoOtraMoneda is not None:
            showIndent(outfile, level, pretty_print)
            outfile.write(bytes(('<MontoExentoOtraMoneda>%s</MontoExentoOtraMoneda>%s' % (
                self.gds_format_float(self.MontoExentoOtraMoneda, input_name='MontoExentoOtraMoneda'), eol_)).encode()))
        if self.TotalITBISOtraMoneda is not None:
            showIndent(outfile, level, pretty_print)
            outfile.write(bytes(('<TotalITBISOtraMoneda>%s</TotalITBISOtraMoneda>%s' % (
                self.gds_format_float(self.TotalITBISOtraMoneda, input_name='TotalITBISOtraMoneda'), eol_)).encode()))
        if self.TotalITBIS1OtraMoneda is not None:
            showIndent(outfile, level, pretty_print)
            outfile.write(bytes(('<TotalITBIS1OtraMoneda>%s</TotalITBIS1OtraMoneda>%s' % (
                self.gds_format_float(self.TotalITBIS1OtraMoneda, input_name='TotalITBIS1OtraMoneda'), eol_)).encode()))
        if self.TotalITBIS2OtraMoneda is not None:
            showIndent(outfile, level, pretty_print)
            outfile.write(bytes(('<TotalITBIS2OtraMoneda>%s</TotalITBIS2OtraMoneda>%s' % (
                self.gds_format_float(self.TotalITBIS2OtraMoneda, input_name='TotalITBIS2OtraMoneda'), eol_)).encode()))
        if self.TotalITBIS3OtraMoneda is not None:
            showIndent(outfile, level, pretty_print)
            outfile.write(bytes(('<TotalITBIS3OtraMoneda>%s</TotalITBIS3OtraMoneda>%s' % (
                self.gds_format_float(self.TotalITBIS3OtraMoneda, input_name='TotalITBIS3OtraMoneda'), eol_)).encode()))
        if self.MontoImpuestoAdicionalOtraMoneda is not None:
            showIndent(outfile, level, pretty_print)
            outfile.write(bytes(('<MontoImpuestoAdicionalOtraMoneda>%s</MontoImpuestoAdicionalOtraMoneda>%s' % (
                self.gds_format_float(self.MontoImpuestoAdicionalOtraMoneda,
                                      input_name='Monto del Impuesto Adicional en Otra Moneda'), eol_)).encode()))
        if self.ImpuestosAdicionalesOtraMoneda is not None:
            self.ImpuestosAdicionalesOtraMoneda.export(outfile, level, namespace_,
                                                       name_='ImpuestosAdicionalesOtraMoneda',
                                                       pretty_print=pretty_print)
        if self.MontoTotalOtraMoneda is not None:
            showIndent(outfile, level, pretty_print)
            outfile.write(bytes(('<MontoTotalOtraMoneda>%s</MontoTotalOtraMoneda>%s' % (
                self.gds_format_float(self.MontoTotalOtraMoneda, input_name='MontoTotalOtraMoneda'), eol_)).encode()))


class ImpuestosAdicionales(GeneratedsSuper):
    subclass = None
    superclass = None

    def __init__(self, ImpuestoAdicional=None):
        self.original_tagname_ = None

        if ImpuestoAdicional is None:
            self.ImpuestoAdicional = []
        else:
            self.ImpuestoAdicional = ImpuestoAdicional

    def get_ImpuestoAdicional(self):
        return self.ImpuestoAdicional

    def set_ImpuestoAdicional(self, ImpuestoAdicional):
        self.ImpuestoAdicional = ImpuestoAdicional

    def add_ImpuestoAdicional(self, value):
        self.ImpuestoAdicional.append(value)

    def insert_ImpuestoAdicional_at(self, index, value):
        self.ImpuestoAdicional.insert(index, value)

    def replace_ImpuestoAdicional_at(self, index, value):
        self.ImpuestoAdicional[index] = value

    def hasContent_(self):
        if (
                self.ImpuestoAdicional is not None
        ):
            return True
        else:
            return False

    def export(self, outfile, level, namespace_='', name_='ImpuestosAdicionales', namespacedef_='', pretty_print=True):
        imported_ns_def_ = GenerateDSNamespaceDefs_.get('ImpuestosAdicionales')
        if imported_ns_def_ is not None:
            namespacedef_ = imported_ns_def_
        if pretty_print:
            eol_ = '\n'
        else:
            eol_ = ''
        if self.original_tagname_ is not None:
            name_ = self.original_tagname_
        showIndent(outfile, level, pretty_print)
        outfile.write(bytes(('<%s%s%s' % (namespace_, name_, namespacedef_ and ' ' + namespacedef_ or '',)).encode()))

        if self.hasContent_():
            outfile.write(bytes(('>%s' % (eol_,)).encode()))
            self.exportChildren(outfile, level + 1, namespace_='', name_='ImpuestosAdicionales',
                                pretty_print=pretty_print)
            showIndent(outfile, level, pretty_print)
            outfile.write(bytes(('</%s%s>%s' % (namespace_, name_, eol_)).encode()))
        else:
            outfile.write(bytes(('/>%s' % (eol_,)).encode()))

    def exportChildren(self, outfile, level, namespace_='', name_='DetalleServicioType', fromsubclass_=False,
                       pretty_print=True):
        if pretty_print:
            eol_ = '\n'
        else:
            eol_ = ''
        for LineaImpAd in self.ImpuestoAdicional:
            LineaImpAd.export(outfile, level, namespace_, name_='ImpuestoAdicional', pretty_print=pretty_print)


class ImpuestoAdicional(GeneratedsSuper):
    subclass = None
    superclass = None

    def __init__(self, TipoImpuesto, TasaImpuestoAdicional=None, MontoImpuestoSelectivoConsumoEspecifico=None,
                 MontoImpuestoSelectivoConsumoAdvalorem=None, OtrosImpuestosAdicionales=None):
        self.original_tagname_ = None
        self.TipoImpuesto = TipoImpuesto
        self.TasaImpuestoAdicional = TasaImpuestoAdicional
        self.MontoImpuestoSelectivoConsumoEspecifico = MontoImpuestoSelectivoConsumoEspecifico
        self.MontoImpuestoSelectivoConsumoAdvalorem = MontoImpuestoSelectivoConsumoAdvalorem
        self.OtrosImpuestosAdicionales = OtrosImpuestosAdicionales

    def get_TipoImpuesto(self):
        return self.TipoImpuesto

    def set_TipoImpuesto(self, TipoImpuesto):
        self.TipoImpuesto = TipoImpuesto

    def get_TasaImpuestoAdicional(self):
        return self.TasaImpuestoAdicional

    def set_TasaImpuestoAdicional(self, TasaImpuestoAdicional):
        self.TasaImpuestoAdicional = TasaImpuestoAdicional

    def get_MontoImpuestoSelectivoConsumoEspecifico(self):
        return self.MontoImpuestoSelectivoConsumoEspecifico

    def set_MontoImpuestoSelectivoConsumoEspecifico(self, MontoImpuestoSelectivoConsumoEspecifico):
        self.MontoImpuestoSelectivoConsumoEspecifico = MontoImpuestoSelectivoConsumoEspecifico

    def get_MontoImpuestoSelectivoConsumoAdvalorem(self):
        return self.MontoImpuestoSelectivoConsumoAdvalorem

    def set_MontoImpuestoSelectivoConsumoAdvalorem(self, MontoImpuestoSelectivoConsumoAdvalorem):
        self.MontoImpuestoSelectivoConsumoAdvalorem = MontoImpuestoSelectivoConsumoAdvalorem

    def get_OtrosImpuestosAdicionales(self):
        return self.OtrosImpuestosAdicionales

    def set_OtrosImpuestosAdicionales(self, OtrosImpuestosAdicionales):
        self.OtrosImpuestosAdicionales = OtrosImpuestosAdicionales

    def hasContent_(self):
        if (
                self.TipoImpuesto is not None or
                self.TasaImpuestoAdicional is not None or
                self.MontoImpuestoSelectivoConsumoEspecifico is not None or
                self.MontoImpuestoSelectivoConsumoAdvalorem is not None or
                self.OtrosImpuestosAdicionales is not None
        ):
            return True
        else:
            return False

    def export(self, outfile, level, namespace_='', name_='TipoImpuesto', namespacedef_='', pretty_print=True):
        imported_ns_def_ = GenerateDSNamespaceDefs_.get('TipoImpuesto')
        if imported_ns_def_ is not None:
            namespacedef_ = imported_ns_def_
        if pretty_print:
            eol_ = '\n'
        else:
            eol_ = ''
        if self.original_tagname_ is not None:
            name_ = self.original_tagname_
        showIndent(outfile, level, pretty_print)
        outfile.write(
            bytes(('<%s%s%s' % (namespace_, name_, namespacedef_ and ' ' + namespacedef_ or '',)).encode()))

        if self.hasContent_():
            outfile.write(bytes(('>%s' % (eol_,)).encode()))
            self.exportChildren(outfile, level + 1, namespace_='', name_='TipoImpuesto', pretty_print=pretty_print)
            showIndent(outfile, level, pretty_print)
            outfile.write(bytes(('</%s%s>%s' % (namespace_, name_, eol_)).encode()))
        else:
            outfile.write(bytes(('/>%s' % (eol_,)).encode()))

    def exportChildren(self, outfile, level, namespace_='', name_='EmisorType', fromsubclass_=False,
                       pretty_print=True):
        if pretty_print:
            eol_ = '\n'
        else:
            eol_ = ''
        if self.TipoImpuesto is not None:
            showIndent(outfile, level, pretty_print)
            outfile.write(bytes(('<TipoImpuesto>%s</TipoImpuesto>%s' % (
                self.gds_encode(
                    self.gds_format_string(quote_xml(self.TipoImpuesto), input_name='TipoImpuesto')),
                eol_)).encode()))
        if self.TasaImpuestoAdicional is not None:
            showIndent(outfile, level, pretty_print)
            outfile.write(bytes(('<TasaImpuestoAdicional>%s</TasaImpuestoAdicional>%s' % (
                self.gds_format_float(self.TasaImpuestoAdicional, input_name='TasaImpuestoAdicional'), eol_)).encode()))
        if self.MontoImpuestoSelectivoConsumoEspecifico is not None:
            showIndent(outfile, level, pretty_print)
            outfile.write(
                bytes(('<MontoImpuestoSelectivoConsumoEspecifico>%s</MontoImpuestoSelectivoConsumoEspecifico>%s' % (
                    self.gds_encode(
                        self.gds_format_string(quote_xml(self.MontoImpuestoSelectivoConsumoEspecifico),
                                               input_name='MontoImpuestoSelectivoConsumoEspecifico')),
                    eol_)).encode()))
        if self.MontoImpuestoSelectivoConsumoAdvalorem is not None:
            showIndent(outfile, level, pretty_print)
            outfile.write(
                bytes(('<MontoImpuestoSelectivoConsumoAdvalorem>%s</MontoImpuestoSelectivoConsumoAdvalorem>%s' % (
                    self.gds_format_float(self.MontoImpuestoSelectivoConsumoAdvalorem,
                                          input_name='MontoImpuestoSelectivoConsumoAdvalorem'), eol_)).encode()))
        if self.OtrosImpuestosAdicionales is not None:
            showIndent(outfile, level, pretty_print)
            outfile.write(bytes(('<OtrosImpuestosAdicionales>%s</OtrosImpuestosAdicionales>%s' % (
                self.gds_format_float(self.OtrosImpuestosAdicionales, input_name='OtrosImpuestosAdicionales'),
                eol_)).encode()))


class ImpuestosAdicionalesOtraMoneda(GeneratedsSuper):
    subclass = None
    superclass = None

    def __init__(self, ImpuestoAdicionalOtraMoneda=None):
        self.original_tagname_ = None

        if ImpuestoAdicionalOtraMoneda is None:
            self.ImpuestoAdicionalOtraMoneda = []
        else:
            self.ImpuestoAdicionalOtraMoneda = ImpuestoAdicionalOtraMoneda

    def factory(*args_, **kwargs_):
        if CurrentSubclassModule_ is not None:
            subclass = getSubclassFromModule_(
                CurrentSubclassModule_, ImpuestosAdicionalesOtraMoneda)
            if subclass is not None:
                return subclass(*args_, **kwargs_)
        if ImpuestosAdicionalesOtraMoneda.subclass:
            return ImpuestosAdicionalesOtraMoneda.subclass(*args_, **kwargs_)
        else:
            return ImpuestosAdicionalesOtraMoneda(*args_, **kwargs_)

    factory = staticmethod(factory)

    def get_ImpuestoAdicionalOtraMoneda(self):
        return self.ImpuestoAdicionalOtraMoneda

    def set_ImpuestoAdicionalOtraMoneda(self, ImpuestoAdicionalOtraMoneda):
        self.ImpuestoAdicionalOtraMoneda = ImpuestoAdicionalOtraMoneda

    def add_ImpuestoAdicionalOtraMoneda(self, value):
        self.ImpuestoAdicionalOtraMoneda.append(value)

    def insert_ImpuestoAdicionalOtraMoneda_at(self, index, value):
        self.ImpuestoAdicionalOtraMoneda.insert(index, value)

    def replace_ImpuestoAdicional_at(self, index, value):
        self.ImpuestoAdicionalOtraMoneda[index] = value

    def hasContent_(self):
        if (
                self.ImpuestoAdicionalOtraMoneda is not None
        ):
            return True
        else:
            return False

    def export(self, outfile, level, namespace_='', name_='ImpuestosAdicionalesOtraMoneda', namespacedef_='', pretty_print=True):
        imported_ns_def_ = GenerateDSNamespaceDefs_.get('ImpuestosAdicionalesOtraMoneda')
        if imported_ns_def_ is not None:
            namespacedef_ = imported_ns_def_
        if pretty_print:
            eol_ = '\n'
        else:
            eol_ = ''
        if self.original_tagname_ is not None:
            name_ = self.original_tagname_
        showIndent(outfile, level, pretty_print)
        outfile.write(bytes(('<%s%s%s' % (namespace_, name_, namespacedef_ and ' ' + namespacedef_ or '',)).encode()))

        if self.hasContent_():
            outfile.write(bytes(('>%s' % (eol_,)).encode()))
            self.exportChildren(outfile, level + 1, namespace_='', name_='ImpuestosAdicionales',
                                pretty_print=pretty_print)
            showIndent(outfile, level, pretty_print)
            outfile.write(bytes(('</%s%s>%s' % (namespace_, name_, eol_)).encode()))
        else:
            outfile.write(bytes(('/>%s' % (eol_,)).encode()))

    def exportChildren(self, outfile, level, namespace_='', name_='DetalleServicioType', fromsubclass_=False,
                       pretty_print=True):
        if pretty_print:
            eol_ = '\n'
        else:
            eol_ = ''
        for LineaImpAd in self.ImpuestoAdicionalOtraMoneda:
            LineaImpAd.export(outfile, level, namespace_, name_='ImpuestoAdicionalOtraMoneda', pretty_print=pretty_print)

    def build(self, node):
        for child in node:
            nodeName_ = Tag_pattern_.match(child.tag).groups()[-1]
            self.buildChildren(child, node, nodeName_)
        return self

    def buildChildren(self, child_, node, nodeName_, fromsubclass_=False):
        if nodeName_ == 'ImpuestoAdicionalOtraMoneda':
            obj_ = ImpuestoAdicionalOtraMoneda.factory(None)
            obj_.build(child_)
            self.add_ImpuestoAdicional(obj_)


class ImpuestoAdicionalOtraMoneda(GeneratedsSuper):
    subclass = None
    superclass = None

    def __init__(self, TipoImpuestoOtraMoneda, TasaImpuestoAdicionalOtraMoneda=None, MontoImpuestoSelectivoConsumoEspecificoOtraMoneda=None,
                 MontoImpuestoSelectivoConsumoAdvaloremOtraMoneda=None, OtrosImpuestosAdicionalesOtraMoneda=None):
        self.original_tagname_ = None
        self.TipoImpuestoOtraMoneda = TipoImpuestoOtraMoneda
        self.TasaImpuestoAdicionalOtraMoneda = TasaImpuestoAdicionalOtraMoneda
        self.MontoImpuestoSelectivoConsumoEspecificoOtraMoneda = MontoImpuestoSelectivoConsumoEspecificoOtraMoneda
        self.MontoImpuestoSelectivoConsumoAdvaloremOtraMoneda = MontoImpuestoSelectivoConsumoAdvaloremOtraMoneda
        self.OtrosImpuestosAdicionalesOtraMoneda = OtrosImpuestosAdicionalesOtraMoneda

    def factory(*args_, **kwargs_):
        if CurrentSubclassModule_ is not None:
            subclass = getSubclassFromModule_(
                CurrentSubclassModule_, ImpuestoAdicionalOtraMoneda)
            if subclass is not None:
                return subclass(*args_, **kwargs_)
        if ImpuestoAdicionalOtraMoneda.subclass:
            return ImpuestoAdicionalOtraMoneda.subclass(*args_, **kwargs_)
        else:
            return ImpuestoAdicionalOtraMoneda(*args_, **kwargs_)

    factory = staticmethod(factory)

    def get_TipoImpuestoOtraMoneda(self):
        return self.TipoImpuestoOtraMoneda

    def set_TipoImpuestoOtraMoneda(self, TipoImpuestoOtraMoneda):
        self.TipoImpuestoOtraMoneda = TipoImpuestoOtraMoneda

    def get_TasaImpuestoAdicionalOtraMoneda(self):
        return self.TasaImpuestoAdicionalOtraMoneda

    def set_TasaImpuestoAdicionalOtraMoneda(self, TasaImpuestoAdicionalOtraMoneda):
        self.TasaImpuestoAdicionalOtraMoneda = TasaImpuestoAdicionalOtraMoneda

    def get_MontoImpuestoSelectivoConsumoEspecificoOtraMoneda(self):
        return self.MontoImpuestoSelectivoConsumoEspecificoOtraMoneda

    def set_MontoImpuestoSelectivoConsumoEspecificoOtraMoneda(self, MontoImpuestoSelectivoConsumoEspecificoOtraMoneda):
        self.MontoImpuestoSelectivoConsumoEspecificoOtraMoneda = MontoImpuestoSelectivoConsumoEspecificoOtraMoneda

    def get_MontoImpuestoSelectivoConsumoAdvaloremOtraMoneda(self):
        return self.MontoImpuestoSelectivoConsumoAdvaloremOtraMoneda

    def set_MontoImpuestoSelectivoConsumoAdvaloremOtraMoneda(self, MontoImpuestoSelectivoConsumoAdvaloremOtraMoneda):
        self.MontoImpuestoSelectivoConsumoAdvaloremOtraMoneda = MontoImpuestoSelectivoConsumoAdvaloremOtraMoneda

    def get_OtrosImpuestosAdicionalesOtraMoneda(self):
        return self.OtrosImpuestosAdicionalesOtraMoneda

    def set_OtrosImpuestosAdicionalesOtraMoneda(self, OtrosImpuestosAdicionalesOtraMoneda):
        self.OtrosImpuestosAdicionalesOtraMoneda = OtrosImpuestosAdicionalesOtraMoneda

    def hasContent_(self):
        if (
                self.TipoImpuestoOtraMoneda is not None or
                self.TasaImpuestoAdicionalOtraMoneda is not None or
                self.MontoImpuestoSelectivoConsumoEspecificoOtraMoneda is not None or
                self.MontoImpuestoSelectivoConsumoAdvaloremOtraMoneda is not None or
                self.OtrosImpuestosAdicionalesOtraMoneda is not None
        ):
            return True
        else:
            return False

    def export(self, outfile, level, namespace_='', name_='TipoImpuesto', namespacedef_='', pretty_print=True):
        imported_ns_def_ = GenerateDSNamespaceDefs_.get('TipoImpuesto')
        if imported_ns_def_ is not None:
            namespacedef_ = imported_ns_def_
        if pretty_print:
            eol_ = '\n'
        else:
            eol_ = ''
        if self.original_tagname_ is not None:
            name_ = self.original_tagname_
        showIndent(outfile, level, pretty_print)
        outfile.write(
            bytes(('<%s%s%s' % (namespace_, name_, namespacedef_ and ' ' + namespacedef_ or '',)).encode()))

        if self.hasContent_():
            outfile.write(bytes(('>%s' % (eol_,)).encode()))
            self.exportChildren(outfile, level + 1, namespace_='', name_='TipoImpuesto', pretty_print=pretty_print)
            showIndent(outfile, level, pretty_print)
            outfile.write(bytes(('</%s%s>%s' % (namespace_, name_, eol_)).encode()))
        else:
            outfile.write(bytes(('/>%s' % (eol_,)).encode()))

    def exportChildren(self, outfile, level, namespace_='', name_='EmisorType', fromsubclass_=False,
                       pretty_print=True):
        if pretty_print:
            eol_ = '\n'
        else:
            eol_ = ''
        if self.TipoImpuestoOtraMoneda is not None:
            showIndent(outfile, level, pretty_print)
            outfile.write(bytes(('<TipoImpuestoOtraMoneda>%s</TipoImpuestoOtraMoneda>%s' % (
                self.gds_encode(
                    self.gds_format_string(quote_xml(self.TipoImpuestoOtraMoneda), input_name='Código de Impuesto adicional en Otra Moneda')),
                eol_)).encode()))
        if self.TasaImpuestoAdicionalOtraMoneda is not None:
            showIndent(outfile, level, pretty_print)
            outfile.write(bytes(('<TasaImpuestoAdicionalOtraMoneda>%s</TasaImpuestoAdicionalOtraMoneda>%s' % (
                self.gds_format_float(self.TasaImpuestoAdicionalOtraMoneda, input_name='Tasa de Impuesto adicional en Otra Moneda'), eol_)).encode()))
        if self.MontoImpuestoSelectivoConsumoEspecificoOtraMoneda is not None:
            showIndent(outfile, level, pretty_print)
            outfile.write(
                bytes(('<MontoImpuestoSelectivoConsumoEspecificoOtraMoneda>%s</MontoImpuestoSelectivoConsumoEspecificoOtraMoneda>%s' % (
                    self.gds_encode(
                        self.gds_format_string(quote_xml(self.MontoImpuestoSelectivoConsumoEspecificoOtraMoneda),
                                               input_name='Monto Impuesto Selectivo al Consumo Específico en Otra Moneda')),
                    eol_)).encode()))
        if self.MontoImpuestoSelectivoConsumoAdvaloremOtraMoneda is not None:
            showIndent(outfile, level, pretty_print)
            outfile.write(bytes(('<MontoImpuestoSelectivoConsumoAdvaloremOtraMoneda>%s</MontoImpuestoSelectivoConsumoAdvaloremOtraMoneda>%s' % (
                self.gds_format_float(self.MontoImpuestoSelectivoConsumoAdvaloremOtraMoneda, input_name='Monto Impuesto Selectivo al Consumo Ad Valorem en Otra Moneda'), eol_)).encode()))
        if self.OtrosImpuestosAdicionalesOtraMoneda is not None:
            showIndent(outfile, level, pretty_print)
            outfile.write(bytes(('<OtrosImpuestosAdicionalesOtraMoneda>%s</OtrosImpuestosAdicionalesOtraMoneda>%s' % (
                self.gds_format_float(self.OtrosImpuestosAdicionalesOtraMoneda, input_name='Monto Otros Impuestos Adicionales en Otra Moneda'), eol_)).encode()))

    def build(self, node):
        for child in node:
            nodeName_ = Tag_pattern_.match(child.tag).groups()[-1]
            self.buildChildren(child, node, nodeName_)
        return self

    def buildChildren(self, child_, node, nodeName_, fromsubclass_=False):
        if nodeName_ == 'ipoImpuestoOtraMoneda':
            self.set_TipoImpuestoOtraMoneda(child_.text)
        # elif nodeName_ == 'CodigoItem':
        #     self.set_CodigoItem(child_.text)


class DetallesItems(GeneratedsSuper):
    subclass = None
    superclass = None

    def __init__(self, Item=None):
        self.original_tagname_ = None
        if Item is None:
            self.Item = []
        else:
            self.Item = Item

    def get_Item(self):
        return self.Item

    def set_Item(self, Item):
        self.Item = Item

    def add_Item(self, value):
        self.Item.append(value)

    def insertItem_at(self, index, value):
        self.Item.insert(index, value)

    def replace_Item_at(self, index, value):
        self.Item[index] = value

    def hasContent_(self):
        if self.Item:
            return True
        else:
            return False

    def export(self, outfile, level, namespace_='', name_='DetallesItems', namespacedef_='', pretty_print=True):
        imported_ns_def_ = GenerateDSNamespaceDefs_.get('DetallesItems')
        if imported_ns_def_ is not None:
            namespacedef_ = imported_ns_def_
        if pretty_print:
            eol_ = '\n'
        else:
            eol_ = ''
        if self.original_tagname_ is not None:
            name_ = self.original_tagname_
        showIndent(outfile, level, pretty_print)
        outfile.write(bytes(('<%s%s%s' % (namespace_, name_, namespacedef_ and ' ' + namespacedef_ or '',)).encode()))
        if self.hasContent_():
            outfile.write(bytes(('>%s' % (eol_,)).encode()))
            self.exportChildren(outfile, level + 1, namespace_='', name_='DetallesItems', pretty_print=pretty_print)
            showIndent(outfile, level, pretty_print)
            outfile.write(bytes(('</%s%s>%s' % (namespace_, name_, eol_)).encode()))
        else:
            outfile.write(bytes(('/>%s' % (eol_,)).encode()))

    def exportChildren(self, outfile, level, namespace_='', name_='DetalleServicioType', fromsubclass_=False,
                       pretty_print=True):
        if pretty_print:
            eol_ = '\n'
        else:
            eol_ = ''
        for LineaItem_ in self.Item:
            LineaItem_.export(outfile, level, namespace_, name_='Item', pretty_print=pretty_print)


class Item(GeneratedsSuper):
    subclass = None
    superclass = None

    def __init__(self, NumeroLinea, NombreItem, IndicadorBienoServicio, CantidadItem, PrecioUnitarioItem,
                 MontoItem, IndicadorFacturacion, DescripcionItem=None, UnidadMedida=None, TablaCodigosItem=None,
                 RecargoMonto=None, TablaSubRecargo=None, DescuentoMonto=None, TablaSubDescuento=None,
                 TablaImpuestoAdicional=None):
        self.original_tagname_ = None
        self.NumeroLinea = NumeroLinea
        self.IndicadorFacturacion = IndicadorFacturacion
        self.NombreItem = NombreItem
        self.IndicadorBienoServicio = IndicadorBienoServicio
        self.DescripcionItem = DescripcionItem
        self.CantidadItem = CantidadItem
        self.UnidadMedida = UnidadMedida
        self.PrecioUnitarioItem = PrecioUnitarioItem
        self.MontoItem = MontoItem
        self.TablaCodigosItem = TablaCodigosItem
        self.RecargoMonto = RecargoMonto
        self.TablaSubRecargo = TablaSubRecargo
        self.DescuentoMonto = DescuentoMonto
        self.TablaSubDescuento = TablaSubDescuento
        self.TablaImpuestoAdicional = TablaImpuestoAdicional

    def get_NumeroLinea(self):
        return self.NumeroLinea

    def set_NumeroLinea(self, NumeroLinea):
        self.NumeroLinea = NumeroLinea

    def get_IndicadorFacturacion(self):
        return self.IndicadorFacturacion

    def set_IndicadorFacturacion(self, IndicadorFacturacion):
        self.IndicadorFacturacion = IndicadorFacturacion

    def get_NombreItem(self):
        return self.NombreItem

    def set_NombreItem(self, NombreItem):
        self.NombreItem = NombreItem

    def get_IndicadorBienoServicio(self):
        return self.IndicadorBienoServicio

    def set_IndicadorBienoServicio(self, IndicadorBienoServicio):
        self.IndicadorBienoServicio = IndicadorBienoServicio

    def get_DescripcionItem(self):
        return self.DescripcionItem

    def set_DescripcionItem(self, DescripcionItem):
        self.DescripcionItem = DescripcionItem

    def get_CantidadItem(self):
        return self.CantidadItem

    def set_CantidadItem(self, CantidadItem):
        self.CantidadItem = CantidadItem

    def get_UnidadMedida(self):
        return self.UnidadMedida

    def set_UnidadMedida(self, UnidadMedida):
        self.UnidadMedida = UnidadMedida

    def get_PrecioUnitarioItem(self):
        return self.PrecioUnitarioItem

    def set_PrecioUnitarioItem(self, PrecioUnitarioItem):
        self.PrecioUnitarioItem = PrecioUnitarioItem

    def get_MontoItem(self):
        return self.MontoItem

    def set_MontoItem(self, MontoItem):
        self.MontoItem = MontoItem

    def get_TablaCodigosItem(self):
        return self.TablaCodigosItem

    def set_TablaCodigosItem(self, TablaCodigosItem):
        self.TablaCodigosItem = TablaCodigosItem

    def get_RecargoMonto(self):
        return self.RecargoMonto

    def set_RecargoMonto(self, RecargoMonto):
        self.RecargoMonto = RecargoMonto

    def get_TablaSubRecargo(self):
        return self.TablaSubRecargo

    def set_TablaSubRecargo(self, TablaSubRecargo):
        self.TablaSubRecargo = TablaSubRecargo

    def get_DescuentoMonto(self):
        return self.DescuentoMonto

    def set_DescuentoMonto(self, DescuentoMonto):
        self.DescuentoMonto = DescuentoMonto

    def get_TablaSubDescuento(self):
        return self.TablaSubDescuento

    def set_TablaSubDescuento(self, TablaSubDescuento):
        self.TablaSubDescuento = TablaSubDescuento

    def get_TablaImpuestoAdicional(self):
        return self.TablaImpuestoAdicional

    def set_TablaImpuestoAdicional(self, TablaImpuestoAdicional):
        self.TablaImpuestoAdicional = TablaImpuestoAdicional

    def hasContent_(self):
        if (
                self.NumeroLinea is not None or
                self.IndicadorFacturacion is not None or
                self.NombreItem is not None or
                self.IndicadorBienoServicio is not None or
                self.DescripcionItem is not None or
                self.CantidadItem is not None or
                self.UnidadMedida is not None or
                self.PrecioUnitarioItem is not None or
                self.MontoItem is not None or
                self.DescuentoMonto is not None or
                self.TablaSubDescuento is not None or
                self.TablaCodigosItem is not None or
                self.RecargoMonto is not None or
                self.TablaSubRecargo is not None or
                self.TablaImpuestoAdicional is not None
        ):
            return True
        else:
            return False

    def export(self, outfile, level, namespace_='', name_='ItemType', namespacedef_='', pretty_print=True):
        imported_ns_def_ = GenerateDSNamespaceDefs_.get('LineaItemType')
        if imported_ns_def_ is not None:
            namespacedef_ = imported_ns_def_
        if pretty_print:
            eol_ = '\n'
        else:
            eol_ = ''
        if self.original_tagname_ is not None:
            name_ = self.original_tagname_
        showIndent(outfile, level, pretty_print)
        outfile.write(bytes(('<%s%s%s' % (namespace_, name_, namespacedef_ and ' ' + namespacedef_ or '',)).encode()))
        if self.hasContent_():
            outfile.write(bytes(('>%s' % (eol_,)).encode()))
            self.exportChildren(outfile, level + 1, namespace_='', name_='ItemType', pretty_print=pretty_print)
            showIndent(outfile, level, pretty_print)
            outfile.write(bytes(('</%s%s>%s' % (namespace_, name_, eol_)).encode()))
        else:
            outfile.write(bytes(('/>%s' % (eol_,)).encode()))

    def exportChildren(self, outfile, level, namespace_='', name_='LineaItemType', fromsubclass_=False,
                       pretty_print=True):
        if pretty_print:
            eol_ = '\n'
        else:
            eol_ = ''
        if self.NumeroLinea is not None:
            showIndent(outfile, level, pretty_print)
            outfile.write(bytes(('<NumeroLinea>%s</NumeroLinea>%s' % (
                self.gds_format_integer(self.NumeroLinea, input_name='NumeroLinea'), eol_)).encode()))
        if self.TablaCodigosItem is not None:
            self.TablaCodigosItem.export(outfile, level, namespace_, name_='TablaCodigosItem',
                                         pretty_print=pretty_print)
        if self.IndicadorFacturacion is not None:
            showIndent(outfile, level, pretty_print)
            outfile.write(bytes(('<IndicadorFacturacion>%s</IndicadorFacturacion>%s' % (
                self.gds_format_integer(self.IndicadorFacturacion, input_name='Indicador de Facturación'),
                eol_)).encode()))
        if self.NombreItem is not None:
            showIndent(outfile, level, pretty_print)
            outfile.write(bytes(('<NombreItem>%s</NombreItem>%s' % (
                self.gds_encode(
                    self.gds_format_string(quote_xml(self.NombreItem), input_name='Nombre del Ítem')),
                eol_)).encode()))
        if self.IndicadorBienoServicio is not None:
            showIndent(outfile, level, pretty_print)
            outfile.write(bytes(('<IndicadorBienoServicio>%s</IndicadorBienoServicio>%s' % (
                self.gds_format_integer(self.IndicadorBienoServicio, input_name='Indicador Bien o Servicio'),
                eol_)).encode()))
        if self.DescripcionItem is not None:
            showIndent(outfile, level, pretty_print)
            outfile.write(bytes(('<DescripcionItem>%s</DescripcionItem>%s' % (
                self.gds_encode(
                    self.gds_format_string(quote_xml(self.DescripcionItem), input_name='Descripción Adicional')),
                eol_)).encode()))
        if self.CantidadItem is not None:
            showIndent(outfile, level, pretty_print)
            outfile.write(bytes(('<CantidadItem>%s</CantidadItem>%s' % (
                self.gds_format_float(self.CantidadItem, input_name='Cantidad'), eol_)).encode()))
        if self.UnidadMedida is not None:
            showIndent(outfile, level, pretty_print)
            outfile.write(bytes(('<UnidadMedida>%s</UnidadMedida>%s' % (
                self.gds_encode(
                    self.gds_format_string(quote_xml(self.UnidadMedida), input_name='Unidad de Medida Ítem')),
                eol_)).encode()))
        if self.PrecioUnitarioItem is not None:
            showIndent(outfile, level, pretty_print)
            outfile.write(bytes(('<PrecioUnitarioItem>%s</PrecioUnitarioItem>%s' % (
                self.gds_format_float(self.PrecioUnitarioItem, input_name='Precio Unitario del Ítem', digits=4),
                eol_)).encode()))
        if self.DescuentoMonto is not None:
            showIndent(outfile, level, pretty_print)
            outfile.write(bytes(('<DescuentoMonto>%s</DescuentoMonto>%s' % (
                self.gds_format_float(self.DescuentoMonto, input_name='DescuentoMonto'),
                eol_)).encode()))
        if self.TablaSubDescuento is not None:
            self.TablaSubDescuento.export(outfile, level, namespace_, name_='TablaSubDescuento',
                                          pretty_print=pretty_print)
        if self.RecargoMonto is not None:
            showIndent(outfile, level, pretty_print)
            outfile.write(bytes(('<RecargoMonto>%s</RecargoMonto>%s' % (
                self.gds_format_float(self.RecargoMonto, input_name='RecargoMonto'), eol_)).encode()))
        if self.TablaSubRecargo is not None:
            self.TablaSubRecargo.export(outfile, level, namespace_, name_='TablaSubRecargo',
                                        pretty_print=pretty_print)
        if self.TablaImpuestoAdicional is not None:
            self.TablaImpuestoAdicional.export(outfile, level, namespace_, name_='TablaImpuestoAdicional',
                                               pretty_print=pretty_print)
        if self.MontoItem is not None:
            showIndent(outfile, level, pretty_print)
            outfile.write(bytes(('<MontoItem>%s</MontoItem>%s' % (
                self.gds_format_float(self.MontoItem, input_name='Monto Ítem'), eol_)).encode()))


class TablaCodigosItem(GeneratedsSuper):
    subclass = None
    superclass = None

    def __init__(self, CodigosItem=None):
        self.original_tagname_ = None

        if CodigosItem is None:
            self.CodigosItem = []
        else:
            self.CodigosItem = CodigosItem

    def get_CodigosItem(self):
        return self.CodigosItem

    def set_CodigosItem(self, CodigosItem):
        self.CodigosItem = CodigosItem

    def add_CodigosItem(self, value):
        self.CodigosItem.append(value)

    def insert_CodigosItem_at(self, index, value):
        self.CodigosItem.insert(index, value)

    def replace_CodigosItem_at(self, index, value):
        self.CodigosItem[index] = value

    def hasContent_(self):
        if self.CodigosItem is not None:
            return True
        else:
            return False

    def export(self, outfile, level, namespace_='', name_='SubcantidadItem', namespacedef_='', pretty_print=True):
        imported_ns_def_ = GenerateDSNamespaceDefs_.get('SubcantidadItem')
        if imported_ns_def_ is not None:
            namespacedef_ = imported_ns_def_
        if pretty_print:
            eol_ = '\n'
        else:
            eol_ = ''
        if self.original_tagname_ is not None:
            name_ = self.original_tagname_
        showIndent(outfile, level, pretty_print)
        outfile.write(bytes(('<%s%s%s' % (namespace_, name_, namespacedef_ and ' ' + namespacedef_ or '',)).encode()))
        if self.hasContent_():
            outfile.write(bytes(('>%s' % (eol_,)).encode()))
            self.exportChildren(outfile, level + 1, namespace_='', name_='SubcantidadItem', pretty_print=pretty_print)
            showIndent(outfile, level, pretty_print)
            outfile.write(bytes(('</%s%s>%s' % (namespace_, name_, eol_)).encode()))
        else:
            outfile.write(bytes(('/>%s' % (eol_,)).encode()))

    def exportChildren(self, outfile, level, namespace_='', name_='DetalleServicioType', fromsubclass_=False,
                       pretty_print=True):
        if pretty_print:
            eol_ = '\n'
        else:
            eol_ = ''
        for LineaItem in self.CodigosItem:
            LineaItem.export(outfile, level, namespace_, name_='CodigosItem', pretty_print=pretty_print)


class CodigosItem(GeneratedsSuper):
    subclass = None
    superclass = None

    def __init__(self, TipoCodigo=None, CodigoItem=None):
        self.original_tagname_ = None
        self.TipoCodigo = TipoCodigo
        self.CodigoItem = CodigoItem

    def get_TipoCodigo(self):
        return self.TipoCodigo

    def set_TipoCodigo(self, TipoCodigo):
        self.TipoCodigo = TipoCodigo

    def get_CodigoItem(self):
        return self.CodigoItem

    def set_CodigoItem(self, CodigoItem):
        self.CodigoItem = CodigoItem

    def hasContent_(self):
        if (
                self.TipoCodigo is not None or
                self.CodigoItem is not None
        ):
            return True
        else:
            return False

    def export(self, outfile, level, namespace_='', name_='TipoImpuesto', namespacedef_='', pretty_print=True):
        imported_ns_def_ = GenerateDSNamespaceDefs_.get('TipoImpuesto')
        if imported_ns_def_ is not None:
            namespacedef_ = imported_ns_def_
        if pretty_print:
            eol_ = '\n'
        else:
            eol_ = ''
        if self.original_tagname_ is not None:
            name_ = self.original_tagname_
        showIndent(outfile, level, pretty_print)
        outfile.write(
            bytes(('<%s%s%s' % (namespace_, name_, namespacedef_ and ' ' + namespacedef_ or '',)).encode()))
        if self.hasContent_():
            outfile.write(bytes(('>%s' % (eol_,)).encode()))
            self.exportChildren(outfile, level + 1, namespace_='', name_='TipoImpuesto', pretty_print=pretty_print)
            showIndent(outfile, level, pretty_print)
            outfile.write(bytes(('</%s%s>%s' % (namespace_, name_, eol_)).encode()))
        else:
            outfile.write(bytes(('/>%s' % (eol_,)).encode()))

    def exportChildren(self, outfile, level, namespace_='', name_='EmisorType', fromsubclass_=False,
                       pretty_print=True):
        if pretty_print:
            eol_ = '\n'
        else:
            eol_ = ''
        if self.TipoCodigo is not None:
            showIndent(outfile, level, pretty_print)
            outfile.write(bytes(('<TipoCodigo>%s</TipoCodigo>%s' % (
                self.gds_encode(
                    self.gds_format_string(quote_xml(self.TipoCodigo), input_name='TipoCodigo')),
                eol_)).encode()))
        if self.CodigoItem is not None:
            showIndent(outfile, level, pretty_print)
            outfile.write(bytes(('<CodigoItem>%s</CodigoItem>%s' % (
                self.gds_encode(
                    self.gds_format_string(quote_xml(self.CodigoItem), input_name='CodigoItem')),
                eol_)).encode()))


class TablaSubDescuento(GeneratedsSuper):
    subclass = None
    superclass = None

    def __init__(self, SubDescuento=None):
        self.original_tagname_ = None

        if SubDescuento is None:
            self.SubDescuento = []
        else:
            self.SubDescuento = SubDescuento

    def get_SubDescuento(self):
        return self.SubDescuento

    def set_ImpuestoAdicional(self, SubDescuento):
        self.SubDescuento = SubDescuento

    def add_SubDescuento(self, value):
        self.SubDescuento.append(value)

    def insert_SubDescuento_at(self, index, value):
        self.SubDescuento.insert(index, value)

    def replace_SubDescuento_at(self, index, value):
        self.SubDescuento[index] = value

    def hasContent_(self):
        if self.SubDescuento is not None:
            return True
        else:
            return False

    def export(self, outfile, level, namespace_='', name_='TablaSubDescuento', namespacedef_='', pretty_print=True):
        imported_ns_def_ = GenerateDSNamespaceDefs_.get('TablaSubDescuento')
        if imported_ns_def_ is not None:
            namespacedef_ = imported_ns_def_
        if pretty_print:
            eol_ = '\n'
        else:
            eol_ = ''
        if self.original_tagname_ is not None:
            name_ = self.original_tagname_
        showIndent(outfile, level, pretty_print)
        outfile.write(bytes(('<%s%s%s' % (namespace_, name_, namespacedef_ and ' ' + namespacedef_ or '',)).encode()))
        if self.hasContent_():
            outfile.write(bytes(('>%s' % (eol_,)).encode()))
            self.exportChildren(outfile, level + 1, namespace_='', name_='TablaSubDescuento', pretty_print=pretty_print)
            showIndent(outfile, level, pretty_print)
            outfile.write(bytes(('</%s%s>%s' % (namespace_, name_, eol_)).encode()))
        else:
            outfile.write(bytes(('/>%s' % (eol_,)).encode()))

    def exportChildren(self, outfile, level, namespace_='', name_='DetalleServicioType', fromsubclass_=False,
                       pretty_print=True):
        if pretty_print:
            eol_ = '\n'
        else:
            eol_ = ''
        for LineaSubDescuento in self.SubDescuento:
            LineaSubDescuento.export(outfile, level, namespace_, name_='SubDescuento', pretty_print=pretty_print)


class SubDescuento(GeneratedsSuper):
    subclass = None
    superclass = None

    def __init__(self, TipoSubDescuento, SubDescuentoPorcentaje=None, MontoSubDescuento=None):
        self.original_tagname_ = None
        self.TipoSubDescuento = TipoSubDescuento
        self.SubDescuentoPorcentaje = SubDescuentoPorcentaje
        self.MontoSubDescuento = MontoSubDescuento

    def get_TipoSubDescuento(self):
        return self.TipoSubDescuento

    def set_TipoSubDescuento(self, TipoSubDescuento):
        self.TipoSubDescuento = TipoSubDescuento

    def get_SubDescuentoPorcentaje(self):
        return self.SubDescuentoPorcentaje

    def set_SubDescuentoPorcentaje(self, SubDescuentoPorcentaje):
        self.SubDescuentoPorcentaje = SubDescuentoPorcentaje

    def get_MontoSubDescuento(self):
        return self.MontoSubDescuento

    def set_MontoSubDescuento(self, MontoSubDescuento):
        self.MontoSubDescuento = MontoSubDescuento

    def hasContent_(self):
        if (
                self.TipoSubDescuento is not None or
                self.SubDescuentoPorcentaje is not None or
                self.MontoSubDescuento is not None
        ):
            return True
        else:
            return False

    def export(self, outfile, level, namespace_='', name_='SubDescuento', namespacedef_='', pretty_print=True):
        imported_ns_def_ = GenerateDSNamespaceDefs_.get('SubDescuento')
        if imported_ns_def_ is not None:
            namespacedef_ = imported_ns_def_
        if pretty_print:
            eol_ = '\n'
        else:
            eol_ = ''
        if self.original_tagname_ is not None:
            name_ = self.original_tagname_
        showIndent(outfile, level, pretty_print)
        outfile.write(
            bytes(('<%s%s%s' % (namespace_, name_, namespacedef_ and ' ' + namespacedef_ or '',)).encode()))
        if self.hasContent_():
            outfile.write(bytes(('>%s' % (eol_,)).encode()))
            self.exportChildren(outfile, level + 1, namespace_='', name_='SubDescuento', pretty_print=pretty_print)
            showIndent(outfile, level, pretty_print)
            outfile.write(bytes(('</%s%s>%s' % (namespace_, name_, eol_)).encode()))
        else:
            outfile.write(bytes(('/>%s' % (eol_,)).encode()))

    def exportChildren(self, outfile, level, namespace_='', name_='EmisorType', fromsubclass_=False,
                       pretty_print=True):
        if pretty_print:
            eol_ = '\n'
        else:
            eol_ = ''
        if self.TipoSubDescuento is not None:
            showIndent(outfile, level, pretty_print)
            outfile.write(bytes(('<TipoSubDescuento>%s</TipoSubDescuento>%s' % (
                self.gds_encode(
                    self.gds_format_string(quote_xml(self.TipoSubDescuento), input_name='TipoSubDescuento')),
                eol_)).encode()))
        if self.SubDescuentoPorcentaje is not None:
            showIndent(outfile, level, pretty_print)
            outfile.write(bytes(('<SubDescuentoPorcentaje>%s</SubDescuentoPorcentaje>%s' % (
                self.gds_format_float(self.SubDescuentoPorcentaje, input_name='SubDescuentoPorcentaje'),
                eol_)).encode()))
        if self.MontoSubDescuento is not None:
            showIndent(outfile, level, pretty_print)
            outfile.write(bytes(('<MontoSubDescuento>%s</MontoSubDescuento>%s' % (
                self.gds_format_float(self.MontoSubDescuento, input_name='MontoSubDescuento'),
                eol_)).encode()))


class TablaSubRecargo(GeneratedsSuper):
    subclass = None
    superclass = None

    def __init__(self, SubRecargo=None):
        self.original_tagname_ = None

        if SubRecargo is None:
            self.SubRecargo = []
        else:
            self.SubRecargo = SubRecargo

    def get_SubRecargo(self):
        return self.SubRecargo

    def set_SubRecargo(self, SubRecargo):
        self.SubRecargo = SubRecargo

    def add_SubRecargo(self, value):
        self.SubRecargo.append(value)

    def insert_SubRecargo_at(self, index, value):
        self.SubRecargo.insert(index, value)

    def replace_SubRecargo_at(self, index, value):
        self.SubRecargo[index] = value

    def hasContent_(self):
        if self.SubRecargo is not None:
            return True
        else:
            return False

    def export(self, outfile, level, namespace_='', name_='TablaSubRecargo', namespacedef_='', pretty_print=True):
        imported_ns_def_ = GenerateDSNamespaceDefs_.get('TablaSubRecargo')
        if imported_ns_def_ is not None:
            namespacedef_ = imported_ns_def_
        if pretty_print:
            eol_ = '\n'
        else:
            eol_ = ''
        if self.original_tagname_ is not None:
            name_ = self.original_tagname_
        showIndent(outfile, level, pretty_print)
        outfile.write(bytes(('<%s%s%s' % (namespace_, name_, namespacedef_ and ' ' + namespacedef_ or '',)).encode()))
        if self.hasContent_():
            outfile.write(bytes(('>%s' % (eol_,)).encode()))
            self.exportChildren(outfile, level + 1, namespace_='', name_='TablaSubRecargo', pretty_print=pretty_print)
            showIndent(outfile, level, pretty_print)
            outfile.write(bytes(('</%s%s>%s' % (namespace_, name_, eol_)).encode()))
        else:
            outfile.write(bytes(('/>%s' % (eol_,)).encode()))

    def exportChildren(self, outfile, level, namespace_='', name_='DetalleServicioType', fromsubclass_=False,
                       pretty_print=True):
        if pretty_print:
            eol_ = '\n'
        else:
            eol_ = ''
        for LineaSubRecargo in self.SubRecargo:
            LineaSubRecargo.export(outfile, level, namespace_, name_='SubRecargo', pretty_print=pretty_print)


class SubRecargo(GeneratedsSuper):
    subclass = None
    superclass = None

    def __init__(self, TipoSubRecargo=None, SubRecargoPorcentaje=None, MontoSubRecargo=None):
        self.original_tagname_ = None
        self.TipoSubRecargo = TipoSubRecargo
        self.SubRecargoPorcentaje = SubRecargoPorcentaje
        self.MontoSubRecargo = MontoSubRecargo

    def get_TipoSubRecargo(self):
        return self.TipoSubRecargo

    def set_TipoSubRecargo(self, TipoSubRecargo):
        self.TipoSubRecargo = TipoSubRecargo

    def get_SubRecargoPorcentaje(self):
        return self.SubDescuentoPorcentaje

    def set_SubRecargoPorcentaje(self, SubRecargoPorcentaje):
        self.SubRecargoPorcentaje = SubRecargoPorcentaje

    def get_MontoSubRecargo(self):
        return self.MontoSubRecargo

    def set_MontoSubRecargo(self, MontoSubRecargo):
        self.MontoSubRecargo = MontoSubRecargo

    def hasContent_(self):
        if (
                self.TipoSubRecargo is not None or
                self.SubRecargoPorcentaje is not None or
                self.MontoSubRecargo is not None
        ):
            return True
        else:
            return False

    def export(self, outfile, level, namespace_='', name_='SubDescuento', namespacedef_='', pretty_print=True):
        imported_ns_def_ = GenerateDSNamespaceDefs_.get('SubDescuento')
        if imported_ns_def_ is not None:
            namespacedef_ = imported_ns_def_
        if pretty_print:
            eol_ = '\n'
        else:
            eol_ = ''
        if self.original_tagname_ is not None:
            name_ = self.original_tagname_
        showIndent(outfile, level, pretty_print)
        outfile.write(
            bytes(('<%s%s%s' % (namespace_, name_, namespacedef_ and ' ' + namespacedef_ or '',)).encode()))
        if self.hasContent_():
            outfile.write(bytes(('>%s' % (eol_,)).encode()))
            self.exportChildren(outfile, level + 1, namespace_='', name_='SubDescuento', pretty_print=pretty_print)
            showIndent(outfile, level, pretty_print)
            outfile.write(bytes(('</%s%s>%s' % (namespace_, name_, eol_)).encode()))
        else:
            outfile.write(bytes(('/>%s' % (eol_,)).encode()))

    def exportChildren(self, outfile, level, namespace_='', name_='EmisorType', fromsubclass_=False,
                       pretty_print=True):
        if pretty_print:
            eol_ = '\n'
        else:
            eol_ = ''
        if self.TipoSubRecargo is not None:
            showIndent(outfile, level, pretty_print)
            outfile.write(bytes(('<TipoSubRecargo>%s</TipoSubRecargo>%s' % (
                self.gds_encode(
                    self.gds_format_string(quote_xml(self.TipoSubRecargo), input_name='TipoSubRecargo')),
                eol_)).encode()))
        if self.SubRecargoPorcentaje is not None:
            showIndent(outfile, level, pretty_print)
            outfile.write(bytes(('<SubRecargoPorcentaje>%s</SubRecargoPorcentaje>%s' % (
                self.gds_format_float(self.SubRecargoPorcentaje, input_name='SubRecargoPorcentaje'),
                eol_)).encode()))
        if self.MontoSubRecargo is not None:
            showIndent(outfile, level, pretty_print)
            outfile.write(bytes(('<MontoSubRecargo>%s</MontoSubRecargo>%s' % (
                self.gds_format_float(self.MontoSubRecargo, input_name='MontoSubRecargo'),
                eol_)).encode()))


class DescuentosORecargos(GeneratedsSuper):
    subclass = None
    superclass = None

    def __init__(self, DescuentoItem=None):
        self.original_tagname_ = None
        if DescuentoItem is None:
            self.DescuentoItem = []
        else:
            self.DescuentoItem = DescuentoItem

    def get_DescuentoItem(self):
        return self.DescuentoItem

    def set_DescuentoItem(self, DescuentoItem):
        self.DescuentoItem = DescuentoItem

    def add_DescuentoItem(self, value):
        self.DescuentoItem.append(value)

    def insertDescuentoItem_at(self, index, value):
        self.DescuentoItem.insert(index, value)

    def replace_Item_at(self, index, value):
        self.DescuentoItem[index] = value

    def hasContent_(self):
        if self.DescuentoItem:
            return True
        else:
            return False

    def export(self, outfile, level, namespace_='', name_='DetallesItemType', namespacedef_='', pretty_print=True):
        imported_ns_def_ = GenerateDSNamespaceDefs_.get('DetallesItemType')
        if imported_ns_def_ is not None:
            namespacedef_ = imported_ns_def_
        if pretty_print:
            eol_ = '\n'
        else:
            eol_ = ''
        if self.original_tagname_ is not None:
            name_ = self.original_tagname_
        showIndent(outfile, level, pretty_print)
        outfile.write(bytes(('<%s%s%s' % (namespace_, name_, namespacedef_ and ' ' + namespacedef_ or '',)).encode()))
        if self.hasContent_():
            outfile.write(bytes(('>%s' % (eol_,)).encode()))
            self.exportChildren(outfile, level + 1, namespace_='', name_='DetallesItemType', pretty_print=pretty_print)
            showIndent(outfile, level, pretty_print)
            outfile.write(bytes(('</%s%s>%s' % (namespace_, name_, eol_)).encode()))
        else:
            outfile.write(bytes(('/>%s' % (eol_,)).encode()))

    def exportChildren(self, outfile, level, namespace_='', name_='DetalleServicioType', fromsubclass_=False,
                       pretty_print=True):
        if pretty_print:
            eol_ = '\n'
        else:
            eol_ = ''
        for LineaItem_ in self.DescuentoItem:
            LineaItem_.export(outfile, level, namespace_, name_='DescuentoORecargo', pretty_print=pretty_print)


class DescuentoORecargo(GeneratedsSuper):
    subclass = None
    superclass = None

    def __init__(self, NumeroLinea=None, TipoAjuste=None, DescripcionDescuentooRecargo=None, TipoValor=None,
                 ValorDescuentooRecargo=None, MontoDescuentooRecargo=None, MontoDescuentooRecargoOtraMoneda=None,
                 IndicadorFacturacionDescuentooRecargo=None):
        self.original_tagname_ = None
        self.NumeroLinea = NumeroLinea
        self.MontoDescuentooRecargo = MontoDescuentooRecargo
        self.TipoAjuste = TipoAjuste
        self.TipoValor = TipoValor
        self.DescripcionDescuentooRecargo = DescripcionDescuentooRecargo
        self.ValorDescuentooRecargo = ValorDescuentooRecargo
        self.MontoDescuentooRecargoOtraMoneda = MontoDescuentooRecargoOtraMoneda
        self.IndicadorFacturacionDescuentooRecargo = IndicadorFacturacionDescuentooRecargo

    def get_NumeroLinea(self):
        return self.NumeroLinea

    def set_NumeroLinea(self, NumeroLinea):
        self.NumeroLinea = NumeroLinea

    def get_MontoDescuentooRecargo(self):
        return self.MontoDescuentooRecargo

    def set_MontoDescuentooRecargo(self, MontoDescuentooRecargo):
        self.MontoDescuentooRecargo = MontoDescuentooRecargo

    def get_TipoAjuste(self):
        return self.TipoAjuste

    def set_TipoAjuste(self, TipoAjuste):
        self.TipoAjuste = TipoAjuste

    def get_TipoValor(self):
        return self.TipoValor

    def set_TipoValor(self, TipoValor):
        self.TipoValor = TipoValor

    def hasContent_(self):
        if (
                self.NumeroLinea is not None or
                self.TipoAjuste is not None or
                self.DescripcionDescuentooRecargo is not None or
                self.TipoValor is not None or
                self.ValorDescuentooRecargo is not None or
                self.MontoDescuentooRecargo is not None or
                self.MontoDescuentooRecargoOtraMoneda is not None or
                self.IndicadorFacturacionDescuentooRecargo is not None
        ):
            return True
        else:
            return False

    def export(self, outfile, level, namespace_='', name_='ItemType', namespacedef_='', pretty_print=True):
        imported_ns_def_ = GenerateDSNamespaceDefs_.get('LineaItemType')
        if imported_ns_def_ is not None:
            namespacedef_ = imported_ns_def_
        if pretty_print:
            eol_ = '\n'
        else:
            eol_ = ''
        if self.original_tagname_ is not None:
            name_ = self.original_tagname_
        showIndent(outfile, level, pretty_print)
        outfile.write(bytes(('<%s%s%s' % (namespace_, name_, namespacedef_ and ' ' + namespacedef_ or '',)).encode()))
        if self.hasContent_():
            outfile.write(bytes(('>%s' % (eol_,)).encode()))
            self.exportChildren(outfile, level + 1, namespace_='', name_='ItemType', pretty_print=pretty_print)
            showIndent(outfile, level, pretty_print)
            outfile.write(bytes(('</%s%s>%s' % (namespace_, name_, eol_)).encode()))
        else:
            outfile.write(bytes(('/>%s' % (eol_,)).encode()))

    def exportChildren(self, outfile, level, namespace_='', name_='LineaItemType', fromsubclass_=False,
                       pretty_print=True):
        if pretty_print:
            eol_ = '\n'
        else:
            eol_ = ''
        if self.NumeroLinea is not None:
            showIndent(outfile, level, pretty_print)
            outfile.write(bytes(('<NumeroLinea>%s</NumeroLinea>%s' % (
                self.gds_format_integer(self.NumeroLinea, input_name='NumeroLinea'), eol_)).encode()))
        if self.TipoAjuste is not None:
            showIndent(outfile, level, pretty_print)
            outfile.write(bytes(('<TipoAjuste>%s</TipoAjuste>%s' % (
                self.gds_encode(
                    self.gds_format_string(quote_xml(self.TipoAjuste), input_name='Tipo de Ajuste')),
                eol_)).encode()))
        if self.DescripcionDescuentooRecargo is not None:
            showIndent(outfile, level, pretty_print)
            outfile.write(bytes(('<DescripcionDescuentooRecargo>%s</DescripcionDescuentooRecargo>%s' % (
                self.gds_encode(
                    self.gds_format_string(quote_xml(self.DescripcionDescuentooRecargo),
                                           input_name='DescripcionDescuentooRecargo')),
                eol_)).encode()))
        if self.TipoValor is not None:
            showIndent(outfile, level, pretty_print)
            outfile.write(bytes(('<TipoValor>%s</TipoValor>%s' % (
                self.gds_encode(
                    self.gds_format_string(quote_xml(self.TipoValor), input_name='Tipo de valor')),
                eol_)).encode()))
        if self.ValorDescuentooRecargo is not None:
            showIndent(outfile, level, pretty_print)
            outfile.write(bytes(('<ValorDescuentooRecargo>%s</ValorDescuentooRecargo>%s' % (
                self.gds_format_float(self.ValorDescuentooRecargo, input_name='ValorDescuentooRecargo'),
                eol_)).encode()))
        if self.MontoDescuentooRecargo is not None:
            showIndent(outfile, level, pretty_print)
            outfile.write(bytes(('<MontoDescuentooRecargo>%s</MontoDescuentooRecargo>%s' % (
                self.gds_format_float(self.MontoDescuentooRecargo, input_name='Monto de Descuento o Recargo'),
                eol_)).encode()))
        if self.IndicadorFacturacionDescuentooRecargo is not None:
            showIndent(outfile, level, pretty_print)
            outfile.write(
                bytes(('<IndicadorFacturacionDescuentooRecargo>%s</IndicadorFacturacionDescuentooRecargo>%s' % (
                    self.gds_format_integer(self.IndicadorFacturacionDescuentooRecargo, input_name='NumeroLinea'),
                    eol_)).encode()))
