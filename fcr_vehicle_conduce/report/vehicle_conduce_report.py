from odoo import _, api, models
from odoo.exceptions import UserError


class VehicleConduceOutgoingReport(models.AbstractModel):
    _name = 'report.fcr_vehicle_conduce.report_vehicle_conduce_outgoing'
    _description = 'Conduce de Salida de vehículos'

    @api.model
    def _get_report_values(self, docids, data=None):
        # A direct report request can contain no ids or the same id more than once.
        docids = list(dict.fromkeys(docids or []))
        pickings = self.env['stock.picking'].browse(docids).exists()
        if not pickings or set(pickings.ids) != set(docids):
            raise UserError(_('Seleccione transferencias existentes para imprimir el Conduce de Salida.'))
        # Prepare every document first: never silently omit invalid members of a batch.
        documents = [picking._get_vehicle_conduce_outgoing_values() for picking in pickings]
        return {
            'doc_ids': pickings.ids,
            'doc_model': 'stock.picking',
            'docs': pickings,
            'conduce_documents': documents,
        }
