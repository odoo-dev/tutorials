{
    "name": "Real Estate",
    "version": "1.0",
    "license": "LGPL-3",
    "category": "Real Estate",
    "summary": "Manage properties",
    "depends": ["base_setup", "mail"],
    "data": [
        "report/estate_property_reports.xml",
        "report/estate_property_templates.xml",
        "report/estate_property_sub_templates.xml",
        "security/ir.model.access.csv",
        "views/real_estate_property.xml",
        "views/estate_property_tree_views.xml",
        "views/estate_property_offer_view.xml",
        "views/property_type_views.xml",
        "views/property_tag.xml",
        "views/res_users_view.xml",
        "views/real_estate_menu.xml",
        "data/real.estate.property.type.csv",
    ],
    "demo": [
        "demo/estate_demo.xml",
    ],
    "installable": True,
    "application": True,
    "auto_install": False,
}
