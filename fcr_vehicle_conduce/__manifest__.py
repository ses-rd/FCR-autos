{
    'name': 'FCR - Conduce de vehículos',
    'version': '19.0.1.0.2',
    'summary': 'Conduce de salida desde entregas de vehículos vinculadas a ventas',
    'author': 'SEGU',
    'category': 'Inventory/Inventory',
    'license': 'LGPL-3',
    'depends': ['eg_fleet_product_link', 'sale_stock', 'web'],
    'data': [
        'report/vehicle_conduce_paperformat.xml',
        'report/vehicle_conduce_templates.xml',
        'report/vehicle_conduce_actions.xml',
        'views/stock_picking_views.xml',
    ],
    'installable': True,
    'application': False,
}
