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


class AnulacionSecuencias(GeneratedsSuper):
    """Formato Anulación de Secuencias de e-NCF"""
    subclass = None
    superclass = None

    def __init__(self, Encabezado, DetalleAnulacion=None):
        self.original_tagname_ = None
        self.Encabezado = Encabezado
        self.DetalleAnulacion = DetalleAnulacion

    def get_Encabezado(self):
        return self.Encabezado

    def set_Encabezado(self, Encabezado):
        self.Encabezado = Encabezado

    def get_DetalleAnulacion(self):
        return self.DetalleAnulacion

    def set_DetalleAnulacion(self, DetalleAnulacion):
        self.DetalleAnulacion = DetalleAnulacion

    def hasContent_(self):
        if (
                self.Encabezado is not None or
                self.DetalleAnulacion is not None
        ):
            return True
        else:
            return False

    def export(self, outfile, level, namespace_='', name_='ANECF', namespacedef_='', pretty_print=True):
        imported_ns_def_ = GenerateDSNamespaceDefs_.get('ANECF')
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
            self.exportChildren(outfile, level + 1, namespace_='', name_='ANECF', pretty_print=pretty_print)
            showIndent(outfile, level, pretty_print)
            outfile.write(bytes(('</%s%s>%s' % (namespace_, name_, eol_)).encode()))
        else:
            outfile.write(bytes(('/>%s' % (eol_,)).encode()))

    def exportChildren(self, outfile, level, namespace_='', name_='ANECF', fromsubclass_=False,
                       pretty_print=True):
        if pretty_print:
            eol_ = '\n'
        else:
            eol_ = ''

        if self.Encabezado is not None:
            self.Encabezado.export(outfile, level, namespace_, name_='Encabezado', pretty_print=pretty_print)
        if self.DetalleAnulacion is not None:
            self.DetalleAnulacion.export(outfile, level, namespace_, name_='DetalleAnulacion',
                                         pretty_print=pretty_print)


class Encabezado(GeneratedsSuper):
    subclass = None
    superclass = None

    def __init__(self, Version, RncEmisor, CantidadeNCFAnulados, FechaHoraAnulacioneNCF):
        self.original_tagname_ = None
        self.Version = Version
        self.RncEmisor = RncEmisor
        self.CantidadeNCFAnulados = CantidadeNCFAnulados
        self.FechaHoraAnulacioneNCF = FechaHoraAnulacioneNCF

    def get_Version(self):
        return self.Version

    def set_Version(self, Version):
        self.Version = Version

    def get_RncEmisor(self):
        return self.RncEmisor

    def set_RncEmisor(self, RncEmisor):
        self.RncEmisor = RncEmisor

    def get_CantidadeNCFAnulados(self):
        return self.CantidadeNCFAnulados

    def set_CantidadeNCFAnulados(self, CantidadeNCFAnulados):
        self.CantidadeNCFAnulados = CantidadeNCFAnulados

    def get_FechaHoraAnulacioneNCF(self):
        return self.FechaHoraAnulacioneNCF

    def set_FechaHoraAnulacioneNCF(self, FechaHoraAnulacioneNCF):
        self.FechaHoraAnulacioneNCF = FechaHoraAnulacioneNCF

    def hasContent_(self):
        if (
                self.Version is not None or
                self.RncEmisor is not None or
                self.CantidadeNCFAnulados is not None or
                self.FechaHoraAnulacioneNCF is not None
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
        if self.RncEmisor is not None:
            showIndent(outfile, level, pretty_print)
            outfile.write(bytes(('<RncEmisor>%s</RncEmisor>%s' % (
                self.gds_encode(self.gds_format_string(quote_xml(self.RncEmisor), input_name='RncEmisor')),
                eol_)).encode()))
        if self.CantidadeNCFAnulados is not None:
            showIndent(outfile, level, pretty_print)
            outfile.write(bytes(('<CantidadeNCFAnulados>%s</CantidadeNCFAnulados>%s' % (
                self.gds_encode(
                    self.gds_format_integer(self.CantidadeNCFAnulados, input_name='CantidadeNCFAnulados')),
                eol_)).encode()))
        if self.FechaHoraAnulacioneNCF is not None:
            showIndent(outfile, level, pretty_print)
            outfile.write(bytes(('<FechaHoraAnulacioneNCF>%s</FechaHoraAnulacioneNCF>%s' % (
                self.gds_encode(
                    self.gds_format_string(quote_xml(self.FechaHoraAnulacioneNCF),
                                           input_name='FechaHoraAnulacioneNCF')),
                eol_)).encode()))

    # end class Encabezado


class DetalleAnulacion(GeneratedsSuper):
    subclass = None
    superclass = None

    def __init__(self, Anulacion=None):
        self.original_tagname_ = None
        if Anulacion is None:
            self.Anulacion = []
        else:
            self.Anulacion = Anulacion

    def get_Anulacion(self):
        return self.Anulacion

    def set_Anulacion(self, Anulacion):
        self.Anulacion = Anulacion

    def add_Anulacion(self, value):
        self.Anulacion.append(value)

    def insert_Anulacion_at(self, index, value):
        self.Anulacion.insert(index, value)

    def replace_Anulacion_at(self, index, value):
        self.Anulacion[index] = value

    def hasContent_(self):
        if (
                self.Anulacion is not None
        ):
            return True
        else:
            return False

    def export(self, outfile, level, namespace_='', name_='DetalleAnulacion', namespacedef_='', pretty_print=True):
        imported_ns_def_ = GenerateDSNamespaceDefs_.get('DetalleAnulacion')
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
            self.exportChildren(outfile, level + 1, namespace_='', name_='DetalleAnulacion', pretty_print=pretty_print)
            showIndent(outfile, level, pretty_print)
            outfile.write(bytes(('</%s%s>%s' % (namespace_, name_, eol_)).encode()))
        else:
            outfile.write(bytes(('/>%s' % (eol_,)).encode()))

    def exportChildren(self, outfile, level, namespace_='', name_='DetalleAnulacion', fromsubclass_=False,
                       pretty_print=True):
        if pretty_print:
            eol_ = '\n'
        else:
            eol_ = ''
        for Linea in self.Anulacion:
            Linea.export(outfile, level, namespace_, name_='Anulacion', pretty_print=pretty_print)

    # end class DetalleAnulacion


class Anulacion(GeneratedsSuper):
    subclass = None
    superclass = None

    def __init__(self, NoLinea, TipoeCF, CantidadeNCFAnulados, TablaRangoSecuenciasAnuladaseNCF):
        self.original_tagname_ = None
        self.NoLinea = NoLinea
        self.TipoeCF = TipoeCF
        self.CantidadeNCFAnulados = CantidadeNCFAnulados
        self.TablaRangoSecuenciasAnuladaseNCF = TablaRangoSecuenciasAnuladaseNCF

    def get_NoLinea(self):
        return self.NoLinea

    def set_NoLinea(self, NoLinea):
        self.NoLinea = NoLinea

    def get_TipoeCF(self):
        return self.TipoeCF

    def set_TipoeCF(self, TipoeCF):
        self.TipoeCF = TipoeCF

    def get_CantidadeNCFAnulados(self):
        return self.CantidadeNCFAnulados

    def set_CantidadeNCFAnulados(self, CantidadeNCFAnulados):
        self.CantidadeNCFAnulados = CantidadeNCFAnulados

    def get_TablaRangoSecuenciasAnuladaseNCF(self):
        return self.TablaRangoSecuenciasAnuladaseNCF

    def set_TablaRangoSecuenciasAnuladaseNCF(self, TablaRangoSecuenciasAnuladaseNCF):
        self.TablaRangoSecuenciasAnuladaseNCF = TablaRangoSecuenciasAnuladaseNCF

    def hasContent_(self):
        if (
                self.NoLinea is not None or
                self.TipoeCF is not None or
                self.CantidadeNCFAnulados is not None or
                self.TablaRangoSecuenciasAnuladaseNCF is not None
        ):
            return True
        else:
            return False

    def export(self, outfile, level, namespace_='', name_='Anulacion', namespacedef_='', pretty_print=True):
        imported_ns_def_ = GenerateDSNamespaceDefs_.get('Anulacion')
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
            self.exportChildren(outfile, level + 1, namespace_='', name_='Anulacion', pretty_print=pretty_print)
            showIndent(outfile, level, pretty_print)
            outfile.write(bytes(('</%s%s>%s' % (namespace_, name_, eol_)).encode()))
        else:
            outfile.write(bytes(('/>%s' % (eol_,)).encode()))

    def exportChildren(self, outfile, level, namespace_='', name_='Anulacion', fromsubclass_=False,
                       pretty_print=True):
        if pretty_print:
            eol_ = '\n'
        else:
            eol_ = ''
        if self.NoLinea is not None:
            showIndent(outfile, level, pretty_print)
            outfile.write(bytes(('<NoLinea>%s</NoLinea>%s' % (
                self.gds_format_integer(self.NoLinea, input_name='NoLinea'), eol_)).encode()))
        if self.TipoeCF is not None:
            showIndent(outfile, level, pretty_print)
            outfile.write(bytes(('<TipoeCF>%s</TipoeCF>%s' % (
                self.gds_encode(
                    self.gds_format_string(quote_xml(self.TipoeCF), input_name='MontoPago')),
                eol_)).encode()))
        if self.TablaRangoSecuenciasAnuladaseNCF is not None:
            self.TablaRangoSecuenciasAnuladaseNCF.export(outfile, level, namespace_, name_='TablaRangoSecuenciasAnuladaseNCF', pretty_print=pretty_print)
        if self.CantidadeNCFAnulados is not None:
            showIndent(outfile, level, pretty_print)
            outfile.write(bytes(('<CantidadeNCFAnulados>%s</CantidadeNCFAnulados>%s' % (
                self.gds_format_integer(self.CantidadeNCFAnulados, input_name='CantidadeNCFAnulados'), eol_)).encode()))

    # end class Anulacion


class TablaRangoSecuenciasAnuladaseNCF(GeneratedsSuper):
    subclass = None
    superclass = None

    def __init__(self, Secuencias=None):
        self.original_tagname_ = None
        if Secuencias is None:
            self.Secuencias = []
        else:
            self.Secuencias = Secuencias

    def get_Secuencias(self):
        return self.Secuencias

    def set_Secuencias(self, Secuencias):
        self.Secuencias = Secuencias

    def add_Secuencias(self, value):
        self.Secuencias.append(value)

    def insert_Secuencias_at(self, index, value):
        self.Secuencias.insert(index, value)

    def replace_Secuencias_at(self, index, value):
        self.Secuencias[index] = value

    def hasContent_(self):
        if (
                self.Secuencias is not None
        ):
            return True
        else:
            return False

    def export(self, outfile, level, namespace_='', name_='DetalleAnulacion', namespacedef_='', pretty_print=True):
        imported_ns_def_ = GenerateDSNamespaceDefs_.get('DetalleAnulacion')
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
            self.exportChildren(outfile, level + 1, namespace_='', name_='DetalleAnulacion', pretty_print=pretty_print)
            showIndent(outfile, level, pretty_print)
            outfile.write(bytes(('</%s%s>%s' % (namespace_, name_, eol_)).encode()))
        else:
            outfile.write(bytes(('/>%s' % (eol_,)).encode()))

    def exportChildren(self, outfile, level, namespace_='', name_='DetalleAnulacion', fromsubclass_=False,
                       pretty_print=True):
        if pretty_print:
            eol_ = '\n'
        else:
            eol_ = ''
        for Linea in self.Secuencias:
            Linea.export(outfile, level, namespace_, name_='Secuencias', pretty_print=pretty_print)

    # end class DetalleAnulacion


class Secuencias(GeneratedsSuper):
    subclass = None
    superclass = None

    def __init__(self, SecuenciaeNCFDesde, SecuenciaeNCFHasta):
        self.original_tagname_ = None
        self.SecuenciaeNCFDesde = SecuenciaeNCFDesde
        self.SecuenciaeNCFHasta = SecuenciaeNCFHasta

    def get_SecuenciaeNCFDesde(self):
        return self.SecuenciaeNCFDesde

    def set_SecuenciaeNCFDesde(self, SecuenciaeNCFDesde):
        self.SecuenciaeNCFDesde = SecuenciaeNCFDesde

    def get_SecuenciaeNCFHasta(self):
        return self.SecuenciaeNCFHasta

    def set_SecuenciaeNCFHasta(self, SecuenciaeNCFHasta):
        self.SecuenciaeNCFHasta = SecuenciaeNCFHasta

    def hasContent_(self):
        if (
                self.SecuenciaeNCFDesde is not None or
                self.SecuenciaeNCFHasta is not None
        ):
            return True
        else:
            return False

    def export(self, outfile, level, namespace_='', name_='Anulacion', namespacedef_='', pretty_print=True):
        imported_ns_def_ = GenerateDSNamespaceDefs_.get('Anulacion')
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
            self.exportChildren(outfile, level + 1, namespace_='', name_='Anulacion', pretty_print=pretty_print)
            showIndent(outfile, level, pretty_print)
            outfile.write(bytes(('</%s%s>%s' % (namespace_, name_, eol_)).encode()))
        else:
            outfile.write(bytes(('/>%s' % (eol_,)).encode()))

    def exportChildren(self, outfile, level, namespace_='', name_='Anulacion', fromsubclass_=False,
                       pretty_print=True):
        if pretty_print:
            eol_ = '\n'
        else:
            eol_ = ''

        if self.SecuenciaeNCFDesde is not None:
            showIndent(outfile, level, pretty_print)
            outfile.write(bytes(('<SecuenciaeNCFDesde>%s</SecuenciaeNCFDesde>%s' % (
                self.gds_encode(
                    self.gds_format_string(quote_xml(self.SecuenciaeNCFDesde), input_name='SecuenciaeNCFDesde')),
                eol_)).encode()))
        if self.SecuenciaeNCFHasta is not None:
            showIndent(outfile, level, pretty_print)
            outfile.write(bytes(('<SecuenciaeNCFHasta>%s</SecuenciaeNCFHasta>%s' % (
                self.gds_encode(
                    self.gds_format_string(quote_xml(self.SecuenciaeNCFHasta), input_name='SecuenciaeNCFHasta')),
                eol_)).encode()))

    # end class Anulacion
