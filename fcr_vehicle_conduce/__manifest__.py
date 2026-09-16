{
    'name': 'FCR - Conduce de vehículos',
    'version': '19.0.1.1.0',
    'summary': 'Conduces de entrada y salida para vehículos vinculados a inventario',
    'author': 'SEGU',
    'category': 'Inventory/Inventory',
    'license': 'LGPL-3',
    'depends': ['eg_fleet_product_link', 'purchase_stock', 'sale_stock', 'web'],
    'data': [
        'report/vehicle_conduce_paperformat.xml',
        'report/vehicle_conduce_templates.xml',
        'report/vehicle_conduce_actions.xml',
        'views/stock_picking_views.xml',
    ],
    'installable': True,
    'application': False,
}
