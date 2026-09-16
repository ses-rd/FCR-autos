from odoo import _, api, models
from odoo.exceptions import UserError


class VehicleConduceReportMixin(models.AbstractModel):
    _name = 'report.fcr_vehicle_conduce.mixin'
    _description = 'Utilidades compartidas para conduces de vehículos'

    @api.model
    def _get_conduce_report_values(self, docids, report_title, values_method):
        # A direct report request can contain no ids or the same id more than once.
        docids = list(dict.fromkeys(docids or []))
        pickings = self.env['stock.picking'].browse(docids).exists()
        if not pickings or set(pickings.ids) != set(docids):
            raise UserError(_(
                'Seleccione transferencias existentes para imprimir %(report_title)s.',
                report_title=report_title,
            ))
        # Prepare every document first: never silently omit invalid members of a batch.
        documents = [getattr(picking, values_method)() for picking in pickings]
        return {
            'doc_ids': pickings.ids,
            'doc_model': 'stock.picking',
            'docs': pickings,
            'conduce_documents': documents,
        }


class VehicleConduceOutgoingReport(models.AbstractModel):
    _name = 'report.fcr_vehicle_conduce.report_vehicle_conduce_outgoing'
    _description = 'Conduce de Salida de vehículos'
    _inherit = 'report.fcr_vehicle_conduce.mixin'

    @api.model
    def _get_report_values(self, docids, data=None):
        return self._get_conduce_report_values(
            docids, _('el Conduce de Salida'), '_get_vehicle_conduce_outgoing_values',
        )


class VehicleConduceIncomingReport(models.AbstractModel):
    _name = 'report.fcr_vehicle_conduce.report_vehicle_conduce_incoming'
    _description = 'Conduce de Entrada de vehículos'
    _inherit = 'report.fcr_vehicle_conduce.mixin'

    @api.model
    def _get_report_values(self, docids, data=None):
        return self._get_conduce_report_values(
            docids, _('el Conduce de Entrada'), '_get_vehicle_conduce_incoming_values',
        )
