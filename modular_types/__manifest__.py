{
    "name": "Modular Types",
    "version": "1.0",
    "depends": ["base", "product", "mrp", "sale_management"],
    "category": "Manufacturing/Manufacturing",
    "data": [
        "security/ir.model.access.csv",
        "wizard/modular_type_wizard_views.xml",
        "views/sale_order_views.xml",
        "views/mrp_bom_line_views.xml",
        "views/product_views.xml",
        "views/mrp_production_views.xml",
    ],
    "sequence": 1,
    "application": True,
    "license": "OEEL-1",
}
