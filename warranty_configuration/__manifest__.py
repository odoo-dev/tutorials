{
    "name": "Warranty Configuration",
    "version": "1.0",
    "depends": ["base", "sale_management", "stock"],
    "data": [
        "wizard/warranty_wizard_views.xml",
        "views/warranty_views.xml",
        "views/warranty_menus.xml",
        "security/ir.model.access.csv",
    ],
    "installable": True,
    "application": False,
    "license": "LGPL-3",
}