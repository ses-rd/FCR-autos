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


class GastosMenoresElectronico(GeneratedsSuper):
    """Elemento Raiz de la Gastos Menores Electrónico"""
    subclass = None
    superclass = None

    def __init__(self, Encabezado, DetallesItems=None, FechaHoraFirma=None):
        self.original_tagname_ = None
        self.Encabezado = Encabezado
        self.DetallesItems = DetallesItems
        self.FechaHoraFirma = FechaHoraFirma

    def get_Encabezado(self):
        return self.Encabezado

    def set_Encabezado(self, Encabezado):
        self.Encabezado = Encabezado

    def get_DetallesItems(self):
        return self.DetallesItems

    def set_DetallesItems(self, DetallesItems):
        self.DetallesItems = DetallesItems

    def get_FechaHoraFirma(self):
        return self.FechaHoraFirma

    def set_FechaHoraFirma(self, FechaHoraFirma):
        self.FechaHoraFirma = FechaHoraFirma

    def hasContent_(self):
        if (
                self.Encabezado is not None or
                self.DetallesItems is not None or
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
        if self.FechaHoraFirma is not None:
            showIndent(outfile, level, pretty_print)
            outfile.write(bytes(('<FechaHoraFirma>%s</FechaHoraFirma>%s' % (
                self.gds_encode(
                    self.gds_format_string(quote_xml(self.FechaHoraFirma), input_name='FechaHoraFirma')),
                eol_)).encode()))


class Encabezado(GeneratedsSuper):
    subclass = None
    superclass = None

    def __init__(self, Version, IdDoc, Emisor, Totales, OtraMoneda=None):
        self.original_tagname_ = None
        self.Version = Version
        self.IdDoc = IdDoc
        self.Emisor = Emisor
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
        if self.Totales is not None:
            self.Totales.export(outfile, level, namespace_, name_='Totales', pretty_print=pretty_print)
        if self.OtraMoneda is not None:
            self.OtraMoneda.export(outfile, level, namespace_, name_='OtraMoneda', pretty_print=pretty_print)


class IdDoc(GeneratedsSuper):
    subclass = None
    superclass = None

    def __init__(self, TipoeCF, eNCF, FechaVencimientoSecuencia, TipoPago=None):
        self.original_tagname_ = None
        self.TipoeCF = TipoeCF
        self.eNCF = eNCF
        self.FechaVencimientoSecuencia = FechaVencimientoSecuencia
        self.TipoPago = TipoPago

    def get_TipoeCF(self):
        return self.TipoeCF

    def set_TipoeCF(self, TipoeCF):
        self.TipoeCF = TipoeCF

    def get_eNCF(self):
        return self.eNCF

    def set_eNCF(self, eNCF):
        self.eNCF = eNCF

    def get_FechaVencimientoSecuencia(self):
        return self.FechaVencimientoSecuencia

    def set_FechaVencimientoSecuencia(self, FechaVencimientoSecuencia):
        self.FechaVencimientoSecuencia = FechaVencimientoSecuencia

    def get_TipoPago(self):
        return self.TipoPago

    def set_TipoPago(self, TipoPago):
        self.TipoPago = TipoPago

    def hasContent_(self):
        if (
                self.TipoeCF is not None or
                self.eNCF is not None or
                self.FechaVencimientoSecuencia is not None or
                self.TipoPago is not None
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
        if self.FechaVencimientoSecuencia is not None:
            showIndent(outfile, level, pretty_print)
            outfile.write(bytes(('<FechaVencimientoSecuencia>%s</FechaVencimientoSecuencia>%s' % (
                self.gds_format_date(self.FechaVencimientoSecuencia, input_name='FechaVencimientoSecuencia'),
                eol_)).encode()))
        if self.TipoPago is not None:
            showIndent(outfile, level, pretty_print)
            outfile.write(bytes(('<TipoPago>%s</TipoPago>%s' % (
                self.gds_encode(
                    self.gds_format_string(quote_xml(self.TipoPago), input_name='TipoPago')),
                eol_)).encode()))


class Emisor(GeneratedsSuper):
    subclass = None
    superclass = None

    def __init__(self, RNCEmisor, RazonSocialEmisor, DireccionEmisor, FechaEmision, NombreComercial=None, Sucursal=None,
                 CorreoEmisor=None, Provincia=None, Municipio=None, WebSite=None, ZonaVenta=None,
                 NumeroFacturaInterna=None, NumeroPedidoInterno=None, TablaTelefonoEmisor=None, InformacionAdicionalEmisor=None):
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

    def get_ZonaVenta(self):
        return self.ZonaVenta

    def get_NumeroFacturaInterna(self):
        return self.NumeroFacturaInterna

    def set_NumeroFacturaInterna(self, NumeroFacturaInterna):
        self.NumeroFacturaInterna = NumeroFacturaInterna

    def get_NumeroPedidoInterno(self):
        return self.NumeroPedidoInterno

    def set_NumeroPedidoInterno(self, NumeroPedidoInterno):
        self.NumeroPedidoInterno = NumeroPedidoInterno

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
                self.NumeroFacturaInterna is not None or
                self.NumeroPedidoInterno is not None or
                self.ZonaVenta is not None or
                self.TablaTelefonoEmisor is not None or
                self.InformacionAdicionalEmisor is not None
        ):
            return True
        else:
            return False

    def export(self, outfile, level, namespace_='', name_='Emisor', namespacedef_='', pretty_print=True):
        imported_ns_def_ = GenerateDSNamespaceDefs_.get('Emisor')
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
            self.exportChildren(outfile, level + 1, namespace_='', name_='Emisor', pretty_print=pretty_print)
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

    def exportChildren(self, outfile, level, namespace_='', name_='TablaTelefonoEmisor', fromsubclass_=False,
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


class Totales(GeneratedsSuper):
    subclass = None
    superclass = None

    def __init__(self, MontoTotal, MontoExento=0.00, MontoImpuestoAdicional=None,
                 ImpuestosAdicionales=None, ValorPagar=None, TotalITBISRetenido=None, TotalISRRetencion=None):
        self.original_tagname_ = None
        self.MontoExento = MontoExento
        self.MontoTotal = MontoTotal
        self.MontoImpuestoAdicional = MontoImpuestoAdicional
        self.ImpuestosAdicionales = ImpuestosAdicionales
        self.ValorPagar = ValorPagar
        self.TotalITBISRetenido = TotalITBISRetenido
        self.TotalISRRetencion = TotalISRRetencion

    def get_MontoExento(self):
        return self.MontoExento

    def set_MontoExento(self, MontoExento):
        self.MontoExento = MontoExento

    def get_MontoTotal(self):
        return self.MontoTotal

    def set_MontoTotal(self, MontoTotal):
        self.MontoTotal = MontoTotal

    def get_MontoImpuestoAdicional(self):
        return self.MontoImpuestoAdicional

    def set_MontoImpuestoAdicional(self, MontoImpuestoAdicional):
        self.MontoImpuestoAdicional = MontoImpuestoAdicional

    def get_ImpuestosAdicionales(self):
        return self.ImpuestosAdicionales

    def set_ImpuestosAdicionales(self, ImpuestosAdicionales):
        self.ImpuestosAdicionales = ImpuestosAdicionales

    def get_ValorPagar(self):
        return self.ValorPagar

    def set_ValorPagar(self, ValorPagar):
        self.ValorPagar = ValorPagar

    def get_TotalITBISRetenido(self):
        return self.TotalITBISRetenido

    def set_TotalITBISRetenido(self, TotalITBISRetenido):
        self.TotalITBISRetenido = TotalITBISRetenido

    def get_TotalISRRetencion(self):
        return self.TotalISRRetencion

    def set_TotalISRRetencion(self, TotalISRRetencion):
        self.TotalISRRetencion = TotalISRRetencion

    def hasContent_(self):
        if (
                self.MontoExento is not None or
                self.MontoTotal is not None or
                self.MontoImpuestoAdicional is not None or
                self.ImpuestosAdicionales is not None or
                self.ValorPagar is not None or
                self.TotalITBISRetenido is not None or
                self.TotalISRRetencion is not None
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

        if self.MontoExento is not None:
            showIndent(outfile, level, pretty_print)
            outfile.write(bytes(('<MontoExento>%s</MontoExento>%s' % (
                self.gds_format_float(self.MontoExento, input_name='Monto Exento'), eol_)).encode()))
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
        if self.TotalITBISRetenido is not None:
            showIndent(outfile, level, pretty_print)
            outfile.write(bytes(('<TotalITBISRetenido>%s</TotalITBISRetenido>%s' % (
                self.gds_format_float(self.TotalITBISRetenido, input_name='TotalITBISRetenido'), eol_)).encode()))
        if self.TotalISRRetencion is not None:
            showIndent(outfile, level, pretty_print)
            outfile.write(bytes(('<TotalISRRetencion>%s</TotalISRRetencion>%s' % (
                self.gds_format_float(self.TotalISRRetencion, input_name='TotalISRRetencion'), eol_)).encode()))


class OtraMoneda(GeneratedsSuper):
    subclass = None
    superclass = None

    def __init__(self, TipoMoneda=None, TipoCambio=None, MontoExentoOtraMoneda=0.00, MontoTotalOtraMoneda=None):
        self.original_tagname_ = None
        self.TipoMoneda = TipoMoneda
        self.TipoCambio = TipoCambio
        self.MontoExentoOtraMoneda = MontoExentoOtraMoneda
        self.MontoTotalOtraMoneda = MontoTotalOtraMoneda

    def get_TipoMoneda(self):
        return self.TipoMoneda

    def set_TipoMoneda(self, TipoMoneda):
        self.TipoMoneda = TipoMoneda

    def get_TipoCambio(self):
        return self.TipoCambio

    def set_TipoCambio(self, TipoCambio):
        self.TipoCambio = TipoCambio

    def get_MontoExentoOtraMoneda(self):
        return self.MontoExentoOtraMoneda

    def set_MontoExentoOtraMoneda(self, MontoExentoOtraMoneda):
        self.MontoExentoOtraMoneda = MontoExentoOtraMoneda

    def get_MontoTotalOtraMoneda(self):
        return self.MontoTotalOtraMoneda

    def set_MontoTotalOtraMoneda(self, MontoTotalOtraMoneda):
        self.MontoTotalOtraMoneda = MontoTotalOtraMoneda

    def hasContent_(self):
        if (
                self.TipoMoneda is not None or
                self.TipoCambio is not None or
                self.MontoExentoOtraMoneda is not None or
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
        if self.MontoExentoOtraMoneda is not None:
            showIndent(outfile, level, pretty_print)
            outfile.write(bytes(('<MontoExentoOtraMoneda>%s</MontoExentoOtraMoneda>%s' % (
                self.gds_format_float(self.MontoExentoOtraMoneda, input_name='MontoExentoOtraMoneda'), eol_)).encode()))
        if self.MontoTotalOtraMoneda is not None:
            showIndent(outfile, level, pretty_print)
            outfile.write(bytes(('<MontoTotalOtraMoneda>%s</MontoTotalOtraMoneda>%s' % (
                self.gds_format_float(self.MontoTotalOtraMoneda, input_name='MontoTotalOtraMoneda'), eol_)).encode()))


class Retencion(GeneratedsSuper):
    subclass = None
    superclass = None

    def __init__(self, IndicadorAgenteRetencionoPercepcion=None, MontoITBISRetenido=None, MontoISRRetenido=None):
        self.original_tagname_ = None
        self.IndicadorAgenteRetencionoPercepcion = IndicadorAgenteRetencionoPercepcion
        self.MontoITBISRetenido = MontoITBISRetenido
        self.MontoISRRetenido = MontoISRRetenido

    def get_IndicadorAgenteRetencionoPercepcion(self):
        return self.IndicadorAgenteRetencionoPercepcion

    def set_IndicadorAgenteRetencionoPercepcion(self, IndicadorAgenteRetencionoPercepcion):
        self.IndicadorAgenteRetencionoPercepcion = IndicadorAgenteRetencionoPercepcion

    def get_MontoITBISRetenido(self):
        return self.MontoITBISRetenido

    def set_MontoITBISRetenido(self, MontoITBISRetenido):
        self.MontoITBISRetenido = MontoITBISRetenido

    def get_MontoISRRetenido(self):
        return self.MontoISRRetenido

    def set_MontoISRRetenido(self, MontoISRRetenido):
        self.MontoISRRetenido = MontoISRRetenido

    def hasContent_(self):
        if (
                self.IndicadorAgenteRetencionoPercepcion is not None or
                self.MontoITBISRetenido is not None or
                self.MontoISRRetenido is not None
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

        if self.IndicadorAgenteRetencionoPercepcion is not None:
            showIndent(outfile, level, pretty_print)
            outfile.write(bytes(('<IndicadorAgenteRetencionoPercepcion>%s</IndicadorAgenteRetencionoPercepcion>%s' % (
                self.gds_format_integer(self.IndicadorAgenteRetencionoPercepcion,
                                        input_name='IndicadorAgenteRetencionoPercepcion'), eol_)).encode()))
        if self.MontoITBISRetenido is not None:
            showIndent(outfile, level, pretty_print)
            outfile.write(bytes(('<MontoITBISRetenido>%s</MontoITBISRetenido>%s' % (
                self.gds_format_float(self.MontoITBISRetenido, input_name='MontoITBISRetenido'), eol_)).encode()))
        if self.MontoISRRetenido is not None:
            showIndent(outfile, level, pretty_print)
            outfile.write(bytes(('<MontoISRRetenido>%s</MontoISRRetenido>%s' % (
                self.gds_format_float(self.MontoISRRetenido, input_name='MontoISRRetenido'), eol_)).encode()))


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
        if self.ImpuestoAdicional is not None:
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

    def export(self, outfile, level, namespace_='', name_='DetallesItem', namespacedef_='', pretty_print=True):
        imported_ns_def_ = GenerateDSNamespaceDefs_.get('DetallesItem')
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
        for LineaItem_ in self.Item:
            LineaItem_.export(outfile, level, namespace_, name_='Item', pretty_print=pretty_print)


class Item(GeneratedsSuper):
    subclass = None
    superclass = None

    def __init__(self, NumeroLinea, NombreItem, IndicadorBienoServicio, CantidadItem, PrecioUnitarioItem,
                 MontoItem, IndicadorFacturacion, DescripcionItem=None, UnidadMedida=None, GradosAlcohol=None,
                 CantidadReferencia=None, UnidadReferencia=None, TablaSubcantidad=None, PrecioUnitarioReferencia=None,
                 TablaImpuestoAdicional=None, DescuentoMonto=None, TablaSubDescuento=None, RecargoMonto=None,
                 TablaSubRecargo=None, Retencion=None, TablaCodigosItem=None):
        self.original_tagname_ = None
        self.NumeroLinea = NumeroLinea
        self.IndicadorFacturacion = IndicadorFacturacion
        self.NombreItem = NombreItem
        self.IndicadorBienoServicio = IndicadorBienoServicio
        self.DescripcionItem = DescripcionItem
        self.CantidadItem = CantidadItem
        self.UnidadMedida = UnidadMedida
        self.CantidadReferencia = CantidadReferencia
        self.UnidadReferencia = UnidadReferencia
        self.TablaSubcantidad = TablaSubcantidad
        self.GradosAlcohol = GradosAlcohol
        self.PrecioUnitarioReferencia = PrecioUnitarioReferencia
        self.PrecioUnitarioItem = PrecioUnitarioItem
        self.DescuentoMonto = DescuentoMonto
        self.MontoItem = MontoItem
        self.TablaImpuestoAdicional = TablaImpuestoAdicional
        self.TablaSubDescuento = TablaSubDescuento
        self.TablaSubRecargo = TablaSubRecargo
        self.RecargoMonto = RecargoMonto
        self.Retencion = Retencion
        self.TablaCodigosItem = TablaCodigosItem

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

    def get_CantidadReferencia(self):
        return self.CantidadReferencia

    def set_CantidadReferencia(self, CantidadReferencia):
        self.CantidadReferencia = CantidadReferencia

    def get_UnidadReferencia(self):
        return self.UnidadReferencia

    def set_UnidadReferencia(self, UnidadReferencia):
        self.UnidadReferencia = UnidadReferencia

    def get_TablaSubcantidad(self):
        return self.TablaSubcantidad

    def set_TablaSubcantidad(self, TablaSubcantidad):
        self.TablaSubcantidad = TablaSubcantidad

    def get_GradosAlcohol(self):
        return self.GradosAlcohol

    def set_GradosAlcohol(self, GradosAlcohol):
        self.GradosAlcohol = GradosAlcohol

    def get_PrecioUnitarioReferencia(self):
        return self.PrecioUnitarioReferencia

    def set_PrecioUnitarioReferencia(self, PrecioUnitarioReferencia):
        self.PrecioUnitarioReferencia = PrecioUnitarioReferencia

    def get_PrecioUnitarioItem(self):
        return self.PrecioUnitarioItem

    def set_PrecioUnitarioItem(self, PrecioUnitarioItem):
        self.PrecioUnitarioItem = PrecioUnitarioItem

    def get_MontoItem(self):
        return self.MontoItem

    def set_MontoItem(self, MontoItem):
        self.MontoItem = MontoItem

    def get_TablaSubDescuento(self):
        return self.TablaSubDescuento

    def set_TablaSubDescuento(self, TablaSubDescuento):
        self.TablaSubDescuento = TablaSubDescuento

    def get_TablaSubRecargo(self):
        return self.TablaSubRecargo

    def set_TablaSubRecargo(self, TablaSubRecargo):
        self.TablaSubRecargo = TablaSubRecargo

    def get_TablaImpuestoAdicional(self):
        return self.TablaImpuestoAdicional

    def set_TablaImpuestoAdicional(self, TablaImpuestoAdicional):
        self.TablaImpuestoAdicional = TablaImpuestoAdicional

    def get_DescuentoMonto(self):
        return self.DescuentoMonto

    def set_DescuentoMonto(self, DescuentoMonto):
        self.DescuentoMonto = DescuentoMonto

    def get_RecargoMonto(self):
        return self.RecargoMonto

    def set_RecargoMonto(self, RecargoMonto):
        self.RecargoMonto = RecargoMonto

    def get_Retencion(self):
        return self.Retencion

    def set_Retencion(self, Retencion):
        self.Retencion = Retencion

    def get_TablaCodigosItem(self):
        return self.TablaCodigosItem

    def set_TablaCodigosItem(self, TablaCodigosItem):
        self.TablaCodigosItem = TablaCodigosItem

    def hasContent_(self):
        if (
                self.NumeroLinea is not None or
                self.IndicadorFacturacion is not None or
                self.NombreItem is not None or
                self.IndicadorBienoServicio is not None or
                self.DescripcionItem is not None or
                self.CantidadItem is not None or
                self.UnidadMedida is not None or
                self.CantidadReferencia is not None or
                self.UnidadReferencia is not None or
                self.TablaSubcantidad is not None or
                self.GradosAlcohol is not None or
                self.PrecioUnitarioReferencia is not None or
                self.PrecioUnitarioItem is not None or
                self.MontoItem is not None or
                self.TablaImpuestoAdicional is not None or
                self.DescuentoMonto is not None or
                self.TablaSubDescuento is not None or
                self.TablaSubRecargo is not None or
                self.RecargoMonto is not None or
                self.TablaCodigosItem is not None or
                self.Retencion is not None
        ):
            return True
        else:
            return False

    def export(self, outfile, level, namespace_='', name_='Iteme', namespacedef_='', pretty_print=True):
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
        if self.Retencion is not None:
            self.Retencion.export(outfile, level, namespace_, name_='Retencion',
                                  pretty_print=pretty_print)
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
        if self.CantidadReferencia is not None:
            showIndent(outfile, level, pretty_print)
            outfile.write(bytes(('<CantidadReferencia>%s</CantidadReferencia>%s' % (
                self.gds_encode(
                    self.gds_format_string(quote_xml(self.CantidadReferencia), input_name='Cantidad de Referencia')),
                eol_)).encode()))
        if self.UnidadReferencia is not None:
            showIndent(outfile, level, pretty_print)
            outfile.write(bytes(('<UnidadReferencia>%s</UnidadReferencia>%s' % (
                self.gds_encode(
                    self.gds_format_string(quote_xml(self.UnidadReferencia), input_name='Unidad de Referencia')),
                eol_)).encode()))
        if self.TablaSubcantidad is not None:
            self.TablaSubcantidad.export(outfile, level, namespace_, name_='TablaSubcantidad',
                                         pretty_print=pretty_print)
        if self.GradosAlcohol is not None:
            showIndent(outfile, level, pretty_print)
            outfile.write(bytes(('<GradosAlcohol>%s</GradosAlcohol>%s' % (
                self.gds_format_float(self.GradosAlcohol, input_name='GradosAlcohol'), eol_)).encode()))
        if self.PrecioUnitarioReferencia is not None:
            showIndent(outfile, level, pretty_print)
            outfile.write(bytes(('<PrecioUnitarioReferencia>%s</PrecioUnitarioReferencia>%s' % (
                self.gds_format_float(self.PrecioUnitarioReferencia, input_name='Precio Unitario de Referencia'),
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
