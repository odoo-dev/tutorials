{
    "name": "warranty1",
    "version": "0.1",
    "license": "LGPL-3",
    "author": "aneg_odoo",
    "depends": ["base", "stock", "sale_management"],
    "description": "Adding warranty",
    "installable": True,
    "application": True,
    "data": [
        "security/ir.model.access.csv",
        "views/inherit_product_template.xml",
        "views/warranty_configuration.xml",
        "views/warranty_menuitem.xml",
        "wizard/add_warranty_action.xml",
        "wizard/add_warranty_button.xml",
    ],
}
