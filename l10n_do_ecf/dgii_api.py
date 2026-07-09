# -*- coding: utf-8 -*-

from io import BytesIO
from lxml import etree
from odoo.http import request
from . import signxml
from odoo.tools.safe_eval import safe_eval
from datetime import datetime
from .models import Semilla
from .models import ARECF
from cryptography.hazmat.primitives.serialization.pkcs12 import load_key_and_certificates
from cryptography.hazmat.primitives import serialization
from werkzeug import urls
import pytz
import subprocess
import urllib3
import ssl
import logging
import requests
import xml.etree.ElementTree as ET
import base64
import tempfile
DGII_VERSION = '1.0'
DGII_NAMESPACE_URL = 'https://dgii.gov.do/cicloContribuyente/facturacion/comprobantesFiscalesElectronicosE-CF/Documentacin%20sobre%20eCF/Formatos%20XML/Formato%20Comprobante%20Fiscal%20Electr%C3%B3nico%20(e-CF)%20V1.0.pdf'

_logger = logging.getLogger(__name__)
parser = etree.XMLParser(remove_blank_text=True)


class CustomHttpAdapter (requests.adapters.HTTPAdapter):
    # "Transport adapter" that allows us to use custom ssl_context.

    def __init__(self, ssl_context=None, **kwargs):
        self.ssl_context = ssl_context
        super().__init__(**kwargs)

    def init_poolmanager(self, connections, maxsize, block=False):
        self.poolmanager = urllib3.poolmanager.PoolManager(
            num_pools=connections, maxsize=maxsize,
            block=block, ssl_context=self.ssl_context)


def get_legacy_session():
    ctx = ssl.create_default_context(ssl.Purpose.SERVER_AUTH)
    ctx.options |= 0x4  # OP_LEGACY_SERVER_CONNECT
    session = requests.session()
    session.mount('https://', CustomHttpAdapter(ctx))
    return session


class DGIIApi:

    def __init__(self, ecf_config=None, cert=None, password=None, environment=None):
        self.cert = cert
        self.password = password
        self.environment = environment
        self.ecf_config = ecf_config
        if ecf_config:
            self.ecf_config = ecf_config
            self.cert = ecf_config.ce_p12_file
            self.password = ecf_config.ce_p12_pin

            # token info
            self._access_token = ecf_config.access_token
            if ecf_config.access_token_expires_in:
                self._token_expires_in = ecf_config.access_token_expires_in
        else:
            self._access_token = None

    def get_ecf_config(self):
        return self.ecf_config

    def _get_pem1(self, certificate):
        # Serializa el certificado en formato PEM
        pem_certificate = certificate.public_bytes(
            encoding=serialization.Encoding.PEM
        )
        return pem_certificate

    def _get_rsa_pkey1(self, private_key):
        # Serializa la clave privada en formato PEM
        pem_key = private_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.TraditionalOpenSSL,
            encryption_algorithm=serialization.NoEncryption()  # O usa una contraseña si es necesario
        )
        return pem_key

    def _expired(self):
        if self._token_expires_in < datetime.now():
            _logger.info("Token expired")
            return True

        return False

    def generate_signature(self, xml_document):
        """Este metodo le aplica la firma digital a un xml.

            :param Elemnt XML xml_document: XML a firmar.
            """

        key1 = base64.b64decode(self.cert)
        private_key, cert, additional_certs = load_key_and_certificates(key1, self.password.encode())
        pkey1 = self._get_rsa_pkey1(private_key)
        pem1 = self._get_pem1(cert)

        signed_root = signxml.XMLSigner(c14n_algorithm="http://www.w3.org/TR/2001/REC-xml-c14n-20010315")
        signed_root.namespaces = {None: signed_root.namespaces['ds']}
        signed = signed_root.sign(
            xml_document,
            key=pkey1,
            cert=pem1
        )
        return etree.tostring(signed, encoding="UTF-8", method="xml", pretty_print=True,
                              doctype='<?xml version="1.0" encoding="UTF-8"?>')

    def _get_semilla(self):
        """Este metodo hace la autenticacion al servicio web de la DGII y retorna una semilla.
        Autenticación:
        Servicio web responsable de generar una sesión para el contribuyente. Retorna el archivo semilla
        (en formato XML) que permitirá obtener el token.

            :returns: XML
            """

        env = self.environment or self.ecf_config.environment
        url_semilla = "https://ecf.dgii.gov.do/{}/autenticacion/api/Autenticacion/Semilla".format(env)
        headers_semilla = {
            "accept": "application/xml"
        }
        try:
            response = get_legacy_session().get(url_semilla, headers=headers_semilla)
            if response.status_code == 200:
                return response.content

            return False
        except requests.exceptions.Timeout as e:
            _logger.warning(f"DGII timeout: {e}")
            return False
        except requests.exceptions.ConnectionError as e:
            _logger.warning(f"DGII connection error: {e}")
            return False
        except requests.exceptions.HTTPError as err:
            _logger.error(err.response.text)
            return False

    def get_token_semilla(self):
        """Este metodo con la semilla previamente obtenida hace un request a la DGII y retorna un token.
        Permite el envío del archivo (Semilla) firmado y retorna un objeto que contiene un string de
        autenticación (token) asociado a una fecha de emisión y una fecha de expiración.

            :returns: JSON
            """

        if self._access_token and not self._expired():
            return {'token': self._access_token}

        env = self.environment or self.ecf_config.environment
        url_val_semilla = "https://ecf.dgii.gov.do/{}/autenticacion/api/Autenticacion/ValidarSemilla".format(env)
        data_xml_document = self._get_semilla()
        if not data_xml_document:
            _logger.error('No se pudo obtener la semilla')
            return False

        try:
            _xml = etree.XML(data_xml_document, parser=parser)
            xml_signature = self.generate_signature(_xml)
            output = BytesIO(xml_signature)
            output.name = "semilla.xml"
            files = {
                'xml': output
            }

            response = get_legacy_session().post(url_val_semilla, files=files)
            json_data = response.json()
            _logger.info(json_data)
            if isinstance(json_data, dict):
                self._access_token = json_data.get('token')
                expire = datetime.strptime(json_data.get('expira'), "%Y-%m-%dT%H:%M:%SZ")
                self._token_expires_in = expire
                if self.ecf_config:
                    self.ecf_config.set_token_data(json_data)
            else:
                return json_data
        except requests.exceptions.Timeout as e:
            _logger.warning(f"DGII timeout: {e}", exc_info=True)
            return "timeout"
        except requests.exceptions.ConnectionError as e:
            _logger.warning(f"DGII connection error: {e}")
            return "connection error"
        except Exception as e:
            _logger.warning(f"error: {e}")
            return "error"
            # return e

        return {'token': json_data['token']}

    def receipt_xml_ecf(self, signed_file: bytes, xmlname: str):
        """Este metodo envia un xml firmado a la DGII.
        Recepción de e‐CF:
        Servicio web responsable de recibir un e‐CF tentativo (XML firmado digitalmente) y un token asociado a una
        sesión válida y en respuesta retornar un objeto que contiene un string denominado TrackId a modo de
        acuse de recibo, con el cual, el contribuyente podrá consultar el estado de su validación.

            :param bytes signed_file: Contenido del xml.
            :param str xmlname: Nombre fichero xml.
            :returns: tuple (response, vals)
            """

        kernel = self.get_token_semilla()
        if not isinstance(kernel, dict):
            return None, {"error": "token_error", "message": "No se pudo obtener el token de autenticación."}

        headers_semilla = {
            "accept": 'application/json',
            'Authorization': 'Bearer {}'.format(kernel.get('token', '')),
        }
        env = self.environment or self.ecf_config.environment
        api_url = 'https://ecf.dgii.gov.do/{}/Recepcion/api/FacturasElectronicas'.format(env)
        _logger.info("##### ENVIANDO A RECEPCION ECF: " + api_url)
        _logger.info("##### ARCHIVO : " + xmlname)
        files = {
            'xml': (xmlname, signed_file.decode(), 'text/xml')
        }
        try:
            response = get_legacy_session().post(api_url, headers=headers_semilla, files=files)
            _logger.info(response.status_code)

            vals = safe_eval(str(response.text).replace("null", "None"))
            vals['token'] = kernel['token']
            return response, vals
        except requests.exceptions.Timeout as e:
            _logger.warning(f"DGII timeout: {e}")
            return None, {"error": "timeout", "message": str(e)}

    def receipt_xml_rfce(self, signed_file: bytes, xmlname: str):
        """Este metodo envia un xml firmado a la DGII.
        Recepción de resumen factura de consumo e-CF:

            :param bytes signed_file: Contenido del xml.
            :param str xmlname: Nombre fichero xml.
            :returns: tuple (response, vals)
            """

        kernel = self.get_token_semilla()
        if not isinstance(kernel, dict):
            return None, {"error": "token_error", "message": "No se pudo obtener el token de autenticación."}

        env = self.environment or self.ecf_config.environment
        headers_semilla = {
            "accept": 'application/xml',
            'Authorization': 'Bearer {}'.format(kernel.get('token', '')),
        }

        api_url = 'https://fc.dgii.gov.do/{}/RecepcionFC/api/Recepcion/ecf'.format(env)
        _logger.info("##### ENVIANDO A RECEPCION RFCE: " + api_url)
        _logger.info("##### FILE : " + xmlname)
        files = {
            'xml': (xmlname, signed_file, 'text/xml')
        }
        try:
            response = get_legacy_session().post(api_url, headers=headers_semilla, files=files)
            _logger.info(response.status_code)
            _logger.info(response.text)

            vals = response.text
            _logger.debug(vals)
            return response, vals
        except requests.exceptions.Timeout as e:
            _logger.warning(f"DGII timeout: {e}")
            return None, {"error": "timeout", "message": str(e)}
        except requests.exceptions.ConnectionError as e:
            _logger.warning(f"DGII connection error: {e}")
            # return "connection error"
            return None, {"error": "connection error", "message": str(e)}
        except Exception as e:
            _logger.warning(f"error: {e}")
            # return "error"
            return None, {"error": "error", "message": str(e)}

    def send_ecf_submit_request_trackId(self, token: str, trackId: str):
        """Este metodo recoge el resultado de un xml previamente enviado a la DGII.
        Servicio web responsable de retornar el estado de procesamiento o validez del e‐CF tentativo enviado
        exclusivamente mediante el servicio web de recepción de e‐CF, a través de la presentación de un Trackid
        y un token asociado a una sesión válida.

            :param str token: Token retornado por el request de envio de xml.
            :param str trackId: trackId retornado por el request de envio de xml.
            """

        env = self.environment or self.ecf_config.environment
        headers_semilla = {
            "accept": 'application/xml',
            'Authorization': 'Bearer {}'.format(token),
        }
        url_params = {
            "TrackId": trackId,
        }
        api_url = f'https://ecf.dgii.gov.do/{env}/ConsultaResultado/api/Consultas/Estado?{urls.url_encode(url_params)}'
        _logger.info("##### ENVIANDO A CONSULTA RESULTADO: " + api_url)
        try:
            response = get_legacy_session().get(api_url, headers=headers_semilla)
            _logger.info(response.status_code)
            _logger.info(response.text)

            vals = response.text
            _logger.debug(vals)
            return response, vals
        except requests.exceptions.Timeout as e:
            _logger.warning(f"DGII timeout: {e}")
            return None, {"error": "timeout", "message": str(e)}

    def send_ecf_status_request(self, rncemisor: str, ncfelectronico: str, rnccomprador: str, codigoseguridad: str):
        """
        Servicio web responsable de responder la validez o estado de un e‐CF a un receptor o incluso a un emisor,
        a través de la presentación del RNC emisor, e‐NCF y dos campos condicionales a la vigencia del comprobante,
        RNC Comprador y el código de seguridad.
        """

        kernel = self.get_token_semilla()
        if not isinstance(kernel, dict):
            return None, {"error": "token_error", "message": "No se pudo obtener el token de autenticación."}

        headers_semilla = {
            "accept": 'application/json',
            'Authorization': 'Bearer {}'.format(kernel.get('token', '')),
        }
        env = self.environment or self.ecf_config.environment
        url_params = {
            "rncemisor": rncemisor,
            "ncfelectronico": ncfelectronico,
            "codigoseguridad": codigoseguridad,
        }
        api_url = f'https://ecf.dgii.gov.do/{env}/consultaestado/api/consultas/estado?{urls.url_encode(url_params)}'

        if rnccomprador:
            url_params.update(rnccomprador=rnccomprador)
            api_url = f'https://ecf.dgii.gov.do/{env}/consultaestado/api/consultas/estado?{urls.url_encode(url_params)}'
        try:
            response = get_legacy_session().get(api_url, headers=headers_semilla)
            _logger.info("##### ENVIANDO A CONSULTA RESULTADO: " + api_url)
            _logger.info(response.status_code)
            _logger.info(response.text)
            vals = response.json()
            return response, vals
        except requests.exceptions.Timeout as e:
            _logger.warning(f"DGII timeout: {e}")
            return None, {"error": "timeout", "message": str(e)}

    def send_consultatrackids(self, rncemisor: str, encf: str):
        """
        Servicio web responsable de retornar un listado de respuestas (Trackids) de un número
        de comprobante fiscal electrónico (e-NCF) que haya sido recibido por DGII, a través de
        la presentación del RNC Emisor, el e-NCF a consultar y un token asociado a una sesión
        válida.
        """

        kernel = self.get_token_semilla()
        if not isinstance(kernel, dict):
            return None, {"error": "token_error", "message": "No se pudo obtener el token de autenticación."}

        headers_semilla = {
            "accept": 'application/json',
            'Authorization': 'Bearer {}'.format(kernel.get('token', '')),
        }
        env = self.environment or self.ecf_config.environment
        url_params = {
            "rncemisor": rncemisor,
            "encf": encf,
        }
        api_url = f'https://ecf.dgii.gov.do/{env}/consultatrackids/api/trackids/consulta?{urls.url_encode(url_params)}'

        response = get_legacy_session().get(api_url, headers=headers_semilla)
        _logger.info("##### ENVIANDO A CONSULTA RESULTADO: " + api_url)
        _logger.info(response.status_code)
        _logger.info(response.text)
        vals = response.json()
        return response, vals

    def send_commercial_approved(self, signed_filename, xmlname):
        """Este metodo envia un xml de Aprobacion Comercial a la DGII.
        Servicio web responsable de recibir aprobaciones comerciales emitidas por contribuyentes receptores,
        la cual consiste en la conformidad con una transacción llevada a cabo entre dos contribuyentes y de la cual
        se recibió un comprobante electrónico de un emisor.

            :param bytes signed_filename: Contenido del xml.
            :param str xmlname: Nombre fichero xml.
            :returns: tuple (response, vals)
            """

        kernel = self.get_token_semilla()
        if not isinstance(kernel, dict):
            return None, {"error": "token_error", "message": "No se pudo obtener el token de autenticación."}

        headers_semilla = {
            "accept": 'application/xml',
            'Authorization': 'Bearer {}'.format(kernel.get('token', '')),
        }
        env = self.environment or self.ecf_config.environment
        api_url = 'https://ecf.dgii.gov.do/{}/AprobacionComercial/api/AprobacionComercial'.format(env)
        _logger.info("##### ENVIANDO A APROBACION COMERCIAL: " + api_url)
        files = {
            'xml': (xmlname, signed_filename.decode(), 'text/xml')
        }

        try:
            response = get_legacy_session().post(api_url, headers=headers_semilla, files=files)
            _logger.info(response.status_code)
            _logger.info(response.text)
            vals = response.text
            return response, vals
        except requests.exceptions.Timeout as e:
            _logger.warning(f"DGII timeout: {e}")
            return None, {"error": "timeout", "message": str(e)}

    def send_anecf_submit_request(self, signed_filename, xmlname):
        """Servicio web responsable de recibir y anular los rangos de secuencias no utilizados
        (e‐NCF) a través de un XML de solicitud que contiene el código de comprobante
        electrónico, una serie de rangos, desde y hasta, así como un token asociado a una
        sesión válida.

            :param bytes signed_filename: Contenido del xml.
            :param str xmlname: Nombre fichero xml.
            :returns: tuple (response, vals)
            """

        kernel = self.get_token_semilla()
        if not isinstance(kernel, dict):
            return False

        headers_semilla = {
            "accept": 'application/json',
            'Authorization': 'Bearer {}'.format(kernel.get('token', '')),
        }
        env = self.ecf_config.environment
        api_url = 'https://ecf.dgii.gov.do/{}/anulacionrangos/api/Operaciones/AnularRango'.format(env)
        _logger.info("##### ENVIANDO A ANECF: " + api_url)
        files = {
            'xml': (xmlname, signed_filename.decode(), 'text/xml')
        }
        try:
            response = get_legacy_session().post(api_url, headers=headers_semilla, files=files)
            _logger.info(response.status_code)
            _logger.info(response.text)
            vals = response.text
            return response, vals
        except requests.exceptions.Timeout as e:
            _logger.warning(f"DGII timeout: {e}")
            return None, {"error": "timeout", "message": str(e)}

    def request_service_by_rnc(self, rnc):
        """Retorna las URLs de los servicios de recepción de eCF,
            aprobación comercial y autenticación (Opcional) de un
            contribuyente en particular, siempre y cuando este autorizado
            como electrónico. """

        kernel = self.get_token_semilla()
        if not isinstance(kernel, dict):
            return False

        headers_semilla = {
            "accept": 'application/json',
            'Authorization': 'Bearer {}'.format(kernel.get('token', '')),
        }
        env = self.ecf_config.environment
        api_url = 'https://ecf.dgii.gov.do/{Environment}/consultadirectorio/api/consultas/obtenerdirectorioporrnc?RNC={rnc}'.format(
            Environment=env,
            rnc=rnc,
        )
        _logger.info("##### ENVIANDO A Consultadirectorio: " + api_url)
        response = get_legacy_session().get(api_url, headers=headers_semilla)
        _logger.info(response.status_code)
        _logger.info(response.text)
        vals = response.json()
        return response, vals

    # === Comunicación Emisor-Receptor ===#

    def authentication_semilla(self):
        """Retorna un archivo semilla (en formato XML) que deberá ser firmado para obtener un token mediante
           el método POST."""

        now = datetime.now(pytz.timezone('America/Santo_Domingo'))
        now = now.replace(microsecond=0)
        classdoc = Semilla
        cedoc = classdoc.SemillaModel(valor=request.csrf_token(), fecha=now)
        file = tempfile.NamedTemporaryFile(delete=False)
        file.write(b'<?xml version="1.0" encoding="utf-8"?>')
        cedoc.export(file, 0, namespacedef_="", pretty_print=False)
        file.write(b'\n')
        file.close()
        file_name = file.name
        xml_f = open(file_name, 'r')
        xml_file = xml_f.read()
        subprocess.call(['rm', '-f', file_name])
        return xml_file

    def return_ARECF(self, xml_data):
        """Retorna un acuse de recibo en formato XML.

            :param str xml_data: Contenido del xml.
            :returns: str
            """

        now = datetime.now(pytz.timezone('America/Santo_Domingo')).strftime("%d-%m-%Y %H:%M:%S")
        classdoc = ARECF
        xml_root = ET.fromstring(xml_data)
        version = xml_root.findall('Encabezado')[0].find('Version').text
        rncemisor = xml_root.findall('Encabezado')[0].findall('Emisor')[0].find('RNCEmisor').text
        encf = xml_root.findall('Encabezado')[0].findall('IdDoc')[0].find('eNCF').text
        rnccomprador = xml_root.findall('Encabezado')[0].findall('Comprador')[0].find('RNCComprador').text
        detalles = classdoc.DetalleAcusedeRecibo(Version=version,
                                                 RNCEmisor=rncemisor,
                                                 eNCF=encf,
                                                 RNCComprador=rnccomprador,
                                                 Estado=0,
                                                 FechaHoraAcuseRecibo=now,
                                                 )

        cedoc = classdoc.AcusedeRecibo(DetalleAcusedeRecibo=detalles)
        file = tempfile.NamedTemporaryFile(delete=False)
        file.write(b'<?xml version="1.0" encoding="utf-8"?>')
        cedoc.export(file, 0, namespacedef_="", pretty_print=False)
        file.write(b'\n')
        file.close()
        file_name = file.name
        xml_f = open(file_name, 'rb')
        xml_file = xml_f.read()
        subprocess.call(['rm', '-f', file_name])
        xml_encoded = bytes(xml_file)
        _xml = etree.XML(xml_encoded, parser=parser)
        xml_signed = self.generate_signature(_xml)
        return xml_signed
