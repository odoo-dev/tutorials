{
    "name": "Product Kit",
    "summary": "A module to create an option to sell a product as kit",
    "depends": ["product", "sale"],
    "author": "Rohit",
    "installable": True,
    "license": "LGPL-3",
    "data": [
        "security/ir.model.access.csv",
        "views/product_template_views.xml",
        "views/sale_order_line_views.xml",
        "views/kit_subproduct_wizard_views.xml",
    ],
}
