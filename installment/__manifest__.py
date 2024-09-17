{
    "name": "Installment",
    "description": "Installment app",
    "version": "0.1",
    "category": "Sales/Sales",
    "depends": ["base", "sale_subscription"],
    "data": [
        "security/ir.model.access.csv",
        "wizard/add_emi_wizard.xml",
        "views/installment_views.xml",
        "views/res_config_settings_views.xml",
        "views/installment_menuitem.xml",
        "data/product_data.xml",
    ],
    "application": True,
    "installable": True,
    "license": "LGPL-3",
}
