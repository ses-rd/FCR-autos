# -*- coding: utf-8 -*-
from odoo import api, fields, models
from datetime import datetime


class FleetVehicle(models.Model):
    _inherit = "fleet.vehicle"

    def _get_year_selection(self):
        current_year = datetime.now().year
        return [(str(i), i) for i in range(1970, current_year + 4)]
