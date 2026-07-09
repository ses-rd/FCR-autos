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


class AprobacionComercial(GeneratedsSuper):
    """Elemento Raiz de la Aprobacion Comercial"""
    subclass = None
    superclass = None

    def __init__(self, DetalleAprobacionComercial):
        self.original_tagname_ = None
        self.DetalleAprobacionComercial = DetalleAprobacionComercial

    def get_DetalleAprobacionComercial(self):
        return self.DetalleAprobacionComercial

    def set_DetalleAprobacionComercial(self, DetalleAprobacionComercial):
        self.DetalleAprobacionComercial = DetalleAprobacionComercial

    def hasContent_(self):
        if (
                self.DetalleAprobacionComercial is not None
        ):
            return True
        else:
            return False

    def export(self, outfile, level, namespace_='', name_='ACECF', namespacedef_='', pretty_print=True):
        imported_ns_def_ = GenerateDSNamespaceDefs_.get('ACECF')
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
            self.exportChildren(outfile, level + 1, namespace_='', name_='ACECF', pretty_print=pretty_print)
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

        if self.DetalleAprobacionComercial is not None:
            self.DetalleAprobacionComercial.export(outfile, level, namespace_, name_='DetalleAprobacionComercial', pretty_print=pretty_print)


class DetalleAprobacionComercial(GeneratedsSuper):
    subclass = None
    superclass = None

    def __init__(self, Version, RNCEmisor, eNCF, FechaEmision, MontoTotal, RNCComprador, Estado,
                 FechaHoraAprobacionComercial, DetalleMotivoRechazo=None):
        self.original_tagname_ = None
        self.Version = Version
        self.RNCEmisor = RNCEmisor
        self.eNCF = eNCF
        self.FechaEmision = FechaEmision
        self.MontoTotal = MontoTotal
        self.RNCComprador = RNCComprador
        self.Estado = Estado
        self.FechaHoraAprobacionComercial = FechaHoraAprobacionComercial
        self.DetalleMotivoRechazo = DetalleMotivoRechazo

    def get_Version(self):
        return self.Version

    def set_Version(self, Version):
        self.Version = Version

    def get_RNCEmisor(self):
        return self.RNCEmisor

    def set_RNCEmisor(self, RNCEmisor):
        self.RNCEmisor = RNCEmisor

    def get_eNCF(self):
        return self.eNCF

    def set_eNCF(self, eNCF):
        self.eNCF = eNCF

    def get_FechaHoraAprobacionComercial(self):
        return self.FechaHoraAprobacionComercial

    def set_FechaHoraAprobacionComercial(self, FechaHoraAprobacionComercial):
        self.FechaHoraAprobacionComercial = FechaHoraAprobacionComercial

    def get_DetalleMotivoRechazo(self):
        return self.DetalleMotivoRechazo

    def set_DetalleMotivoRechazo(self, DetalleMotivoRechazo):
        self.DetalleMotivoRechazo = DetalleMotivoRechazo

    def hasContent_(self):
        if (
                self.Version is not None or
                self.RNCEmisor is not None or
                self.eNCF is not None or
                self.FechaEmision is not None or
                self.MontoTotal is not None or
                self.RNCComprador is not None or
                self.Estado is not None or
                self.FechaHoraAprobacionComercial is not None or
                self.DetalleMotivoRechazo is not None
        ):
            return True
        else:
            return False

    def export(self, outfile, level, namespace_='', name_='ACECF', namespacedef_='', pretty_print=True):
        imported_ns_def_ = GenerateDSNamespaceDefs_.get('ACECF')
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
            self.exportChildren(outfile, level + 1, namespace_='', name_='ACECF', pretty_print=pretty_print)
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

        if self.Version is not None:
            showIndent(outfile, level, pretty_print)
            outfile.write(bytes(('<Version>%s</Version>%s' % (
                self.gds_encode(self.gds_format_string(quote_xml(self.Version), input_name='Version')),
                eol_)).encode()))
        if self.RNCEmisor is not None:
            showIndent(outfile, level, pretty_print)
            outfile.write(bytes(('<RNCEmisor>%s</RNCEmisor>%s' % (
                self.gds_encode(self.gds_format_string(quote_xml(self.RNCEmisor), input_name='RNC Emisor')),
                eol_)).encode()))
        if self.eNCF is not None:
            showIndent(outfile, level, pretty_print)
            outfile.write(bytes(('<eNCF>%s</eNCF>%s' % (
                self.gds_encode(
                    self.gds_format_string(quote_xml(self.eNCF), input_name='eNCF')),
                eol_)).encode()))
        if self.FechaEmision is not None:
            showIndent(outfile, level, pretty_print)
            outfile.write(bytes(('<FechaEmision>%s</FechaEmision>%s' % (
                self.gds_format_date(self.FechaEmision, input_name='FechaEmision'), eol_)).encode()))
        if self.MontoTotal is not None:
            showIndent(outfile, level, pretty_print)
            outfile.write(bytes(('<MontoTotal>%s</MontoTotal>%s' % (
                self.gds_format_float(self.MontoTotal, input_name='Monto Total'), eol_)).encode()))
        if self.RNCComprador is not None:
            showIndent(outfile, level, pretty_print)
            outfile.write(bytes(('<RNCComprador>%s</RNCComprador>%s' % (
                self.gds_encode(self.gds_format_string(quote_xml(self.RNCComprador), input_name='RNC Comprador')),
                eol_)).encode()))
        if self.Estado is not None:
            showIndent(outfile, level, pretty_print)
            outfile.write(bytes(('<Estado>%s</Estado>%s' % (
                self.gds_format_integer(self.Estado, input_name='Estado'), eol_)).encode()))
        if self.DetalleMotivoRechazo is not None:
            showIndent(outfile, level, pretty_print)
            outfile.write(bytes(('<DetalleMotivoRechazo>%s</DetalleMotivoRechazo>%s' % (
                self.gds_encode(
                    self.gds_format_string(quote_xml(self.DetalleMotivoRechazo),
                                           input_name='DetalleMotivoRechazo')),
                eol_)).encode()))
        if self.FechaHoraAprobacionComercial is not None:
            showIndent(outfile, level, pretty_print)
            outfile.write(bytes(('<FechaHoraAprobacionComercial>%s</FechaHoraAprobacionComercial>%s' % (
                self.gds_encode(
                    self.gds_format_string(quote_xml(self.FechaHoraAprobacionComercial),
                                           input_name='FechaHoraAprobacionComercial')),
                eol_)).encode()))
