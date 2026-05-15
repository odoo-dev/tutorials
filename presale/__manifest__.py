{
    "name": "Presale Tutorial",
    "author": "joemo",
    "license": "LGPL-3",
    "application": True,
    "depends": ["base", "base_import_module", "product", "sale_management"],
    "data": [
        "models/presale_order_line.xml",
        "models/presale_order.xml",
        "security/security.xml",
        "security/ir.model.access.csv",
        "views/presale_order_line_views.xml",
        "views/presale_order_views.xml",
        "views/presale_menu.xml",
        "data/ir_cron.xml",
    ],
}
