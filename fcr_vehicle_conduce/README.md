# FCR — Conduces de vehículos (Odoo 19)

Reportes PDF de Entrada y Salida por transferencia, con un único vehículo.
No implementa inspecciones digitales, firmas digitales ni modificaciones de inventario.

## Instalación y dependencias

Instalar `fcr_vehicle_conduce` y sus dependencias `eg_fleet_product_link`, `purchase_stock`,
`sale_stock` y `web`.
`fleet`, `stock`, `product` y `account` llegan mediante esas dependencias.
No depende de `l10n_do_ecf`, facturas ni módulos de nómina.
Los módulos estándar de Odoo no están incluidos en este repositorio.

Configurar dirección, ciudad/provincia, teléfono, correo, web y RNC en la compañía
de la transferencia. El encabezado utiliza esos valores reales, sin sustituir los vacíos
por datos corporativos inventados. El logotipo FCR es el del formato proporcionado.

## Impresión y validaciones

En la cabecera de la transferencia: botones independientes **Conduce de Salida** y
**Conduce de Entrada** cuando aplican.
El botón **Print** estándar se conserva: ejecuta un reporte concreto y no es el
selector de todos los reportes vinculados. El conduce también mantiene su enlace
al menú contextual de reportes, disponible para formulario y lista (`list,form`).
En Odoo 19, `ir.actions.report.domain` filtra ese menú contextual mediante
`get_valid_action_reports`; no convierte el botón Print de la cabecera en un desplegable.
La nueva vista hereda `stock.view_picking_form` y se carga después de la acción.
El botón utiliza `type="action"` y llama directamente al reporte propio; no llama
a `do_print_picking()` ni altera el indicador `printed` del traslado.

## Checklist digital

Los botones **Checklist Conduce de Entrada** y **Checklist Conduce de Salida** abren
o crean un registro `fcr.vehicle.conduce` para la transferencia. La creación reutiliza
las mismas validaciones Python de los PDF: tipo de operación, documento origen, fecha,
contacto y vehículo inequívoco. Si ya existe un conduce del mismo tipo para el picking,
se abre ese mismo registro y no se crean duplicados.

`fcr.vehicle.conduce` guarda la referencia al picking, tipo, compañía, vehículo,
contacto, fecha documental, inspector creador, estado y los checks booleanos del formato
actual. Los permisos se conceden a `stock.group_stock_user` para lectura, creación y
edición; no se usa `sudo()`.

La fase actual no congela todos los datos del vehículo/contacto. Para la fase de firma,
la propuesta es crear campos snapshot editados solo al completar/firmar: nombre/contacto,
identificación, teléfono, correo, campos del vehículo, fecha formateada y textos legales.
El PDF firmado debería leer primero esos snapshots y solo caer a los related actuales si
el conduce sigue en borrador.

El dominio de Salida exige `picking_type_code = outgoing` y estado `assigned` (Listo)
o `done` (Hecho). No exige venta. El dominio de Entrada exige `picking_type_code = incoming`,
`purchase_id` y los mismos estados. El servidor vuelve a validar cada documento,
incluyendo solicitudes directas al reporte. Un lote con una transferencia inválida se
rechaza completo; no se omiten registros silenciosamente.

Se consideran los movimientos no cancelados con demanda positiva antes de finalizar,
o cantidad efectivamente movida positiva después de finalizar. Las líneas canceladas
y cantidades cero no identifican vehículos para este documento.

La venta de Salida es contexto opcional. Si existe una relación estructural inequívoca
por `picking.sale_id`, `move_ids.sale_line_id.order_id` o `reference_ids.sale_ids`, se
incluye en los valores del documento, pero su ausencia no impide generar el conduce. El
destinatario de Salida se toma primero de `picking.partner_id`; la venta solo sirve como
respaldo si el picking no tiene contacto. La compra de Entrada todavía se obtiene de
`move_ids.purchase_line_id.order_id`: debe ser única y coincidir con `picking.purchase_id`.
Ese supuesto queda pendiente de revisión para vehículos en consignación.

El vehículo se obtiene de enlaces explícitos entre producto y Fleet:
`move_ids.product_id.product_tmpl_id.vehicle_id`, `fleet.vehicle.product_id` o
`fleet.vehicle.product_tmpl_id`. No se usa `origin` ni se recorren los productos de toda
la orden de venta o compra.

Se rechazan: ausencia de vehículo, múltiples vehículos distintos, productos `is_fleet`
sin vehículo y diferencias explícitas de compañía. Los productos accesorios sin indicador
Fleet ni vehículo no cuentan como vehículos. No se buscan vehículos adicionales por nombre,
placa o chasis. No se impone unicidad global al módulo Fleet.

La revisión distingue estas condiciones:

| Clase | Regla y motivo |
| --- | --- |
| A: identificación necesaria | Un único vehículo distinto mediante los productos movidos; una venta real única mediante sus líneas. |
| B: inconsistencia bloqueante | Producto marcado `is_fleet` sin vínculo (podría ocultar otro vehículo), diferencias de compañía y línea de venta de un producto distinto al movido. |
| C: dato histórico tolerado | Vehículo archivado, `is_fleet=False` con vínculo válido, varios productos que apuntan al mismo vehículo y enlaces inversos de Fleet vacíos o desactualizados. |

`fleet.vehicle.product_id` y `product_tmpl_id` son campos independientes que el módulo
existente no sincroniza automáticamente. No reemplazan ni invalidan por sí solos el vínculo
desde `product.template.vehicle_id`. Archivado no significa inexistente y no debe impedir
reimprimir. Una compañía vacía en el vehículo se admite como vehículo compartido; una
compañía diferente se rechaza. Se mantienen los permisos normales, sin `sudo()`.

## Mapeo y decisiones

| Dato | Fuente |
| --- | --- |
| Entregado a (Salida) | `picking.partner_id`, después `sale.partner_shipping_id`, después `sale.partner_id` |
| Recibido a (Entrada) | `picking.partner_id`, después `purchase.partner_id` |
| Cédula, teléfono, correo | `vat`, `phone`, `email` del mismo contacto seleccionado |
| Concepto Salida | Texto fijo `ENTREGA DE VEHICULO` |
| Concepto Entrada | Texto fijo `Adquisición FCR` |
| Marca / modelo | `fleet.vehicle.brand_id.name` / `model_id.name` |
| Año / placa / chasis | `model_year` / `license_plate` / `vin_sn` |
| Odómetro | `odometer`, presentado sin decimales; `odometer_unit` como km o mi |
| Color | `color` |
| Tipo provisional | `category_id.name`; si falta, etiqueta traducida de `vehicle_type` (car/bike) |
| Fecha | `date_done` si está Hecho; `scheduled_date` si está Listo |

La regla de fecha está encapsulada en `_get_vehicle_conduce_date()`. Una fecha ausente
produce error. Se convierte a la zona horaria del usuario/contexto y se presenta como
`dd/MM/yyyy`. No se utiliza la fecha actual como sustituto.
Los datos personales ausentes se dejan vacíos; no se mezclan con los del contacto padre.
La selección provisional de Tipo se encapsula en `_get_vehicle_conduce_type(vehicle)`.

El reporte consulta valores actuales: no guarda una fotografía histórica de los datos,
no congela el odómetro y no reutiliza PDFs previamente adjuntados. Imprimir no cambia
el estado del traslado. Una impresión en Listo no acredita una entrega completada.

## Formato y recursos

Carta vertical: 215.9 × 279.4 mm (8.5 × 11 pulgadas). Márgenes superior/inferior
de 10 mm y laterales de 12 mm. Contenido de 164 mm de ancho. Fondo blanco y tinta
oscura para impresión; el fondo oscuro de la captura se interpreta como modo de
visualización. Se reorganizan los datos del vehículo en tres renglones para dejar
espacio a un VIN completo y nombres reales. No se reproducen las X rojas de ejemplo.
Los datos corporativos vacíos se omiten. VIN y correos admiten cortes de palabras largas.
Cada documento tiene su propio artículo y salto de página entre transferencias. No se
recortan datos con `overflow: hidden`: textos arbitrariamente extensos pueden exigir
más de una página; comprobar los casos reales en el motor PDF de Odoo.sh.

El registro específico de `report.paperformat` usa `format = Letter`: Odoo 19 almacena
`page_width` y `page_height` personalizados como enteros, por lo que introducir 215.9
y 279.4 allí truncaría las dimensiones. El formato Letter conserva el tamaño exacto.
Se desactiva `smart shrinking` para respetar las medidas CSS en milímetros y evitar
que wkhtmltopdf reduzca silenciosamente todo el documento.

`static/src/img/vehicle_inspection.png` procede del documento Word de referencia y se
reutiliza en Entrada y Salida para conservar la mejor nitidez disponible. `fcr_logo.png`
procede de la segunda imagen suministrada (Conduce de Salida, 842 × 1079 píxeles):
x=248, y=59, ancho=344, alto=48.

Los textos legales y el pie se transcriben de los formatos suministrados, conservando
su redacción. El checklist y las líneas de Inspector/Cliente se completan a mano.
Encabezado, datos de vehículo, checklist, firmas, pie y estilos son subplantillas
compartidas entre Entrada y Salida.

## Pruebas

En una base **de pruebas** con Odoo 19 y estas dependencias disponibles:

`odoo-bin -d BASE_DE_PRUEBAS -i fcr_vehicle_conduce --test-enable --test-tags /fcr_vehicle_conduce --stop-after-init`

La suite `tests/test_vehicle_conduce.py` utiliza `TransactionCase`, crea sus propios
registros y cubre resolución, errores, fechas, dominio, tamaño de papel y render HTML
QWeb. No depende de S00001, AP/OUT/00002 ni de ningún cliente o vehículo de producción.
Validar también el PDF con wkhtmltopdf y la configuración real de Odoo antes de desplegar.
