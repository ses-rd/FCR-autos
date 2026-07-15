{
    'name': 'Company Seal on Quotations',
    'version': '19.0.1.0.0',
    'summary': 'Adds a company seal field to quotations',
    'category': 'Sales',
    'author': 'SEGU',
    'depends': ['sale'],
    'data': [
        'views/res_company_views.xml',
        'views/sale_order_view.xml',
        'report/report_invoice.xml',
        'report/sale_order_report_templates.xml',
    ],
    'installable': True,
    'application': False,
}
