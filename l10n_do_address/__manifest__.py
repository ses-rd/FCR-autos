# -*- coding: utf-8 -*-
{
    "name": "Topónimos Dominicanos",
    'countries': ['do'],
    "version": "19.0.1.0.0",
    "author": "SEGU",
    "category": "Localization",
    "depends": ["l10n_do_ecf"],
    "license": "LGPL-3",
    "data": [
        'data/res.country.state.csv',
        'data/res.municipality.csv',
        'security/ir.model.access.csv',
        'views/res_partner_views.xml',
    ],
    "auto_install": True,
}
