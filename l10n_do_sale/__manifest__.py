# -*- coding: utf-8 -*-

{
    "name": "Sale Manager República Dominicana",
    'countries': ['do'],
    "summary": "Adaptations to Sales module for Dominican Localization.",
    "description": """
        Agrega el campo tipo de descuento en las líneas de los pedidos de ventas.""",
    "version": "19.0.1.0.0",
    "author": "SEGU",
    "license": "LGPL-3",
    "category": "Localization",
    "depends": ["l10n_do_ecf", "sale_management"],
    "data": [
         "views/sale_order_view.xml",
    ],
    "auto_install": True,
}
