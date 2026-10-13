{
    "name": "FCR - Incoice",
    "version": "19.0.1.8.3",
    "author": "SEGU",
    "category": "Accounting",
    "summary": "Custom invoice",
    "depends": ["l10n_do_ecf", "sale_management"],
    "data": [
        "security/ir.model.access.csv",
        "views/report_invoice.xml",
        "views/product_template_view.xml",
        "views/account_move_views.xml",
        "views/sale_receipt_wizard_views.xml",
        "views/restore_standard_reports.xml",
        "views/sale_order_receipt_report.xml",
    ],
    "license": "LGPL-3",
}
