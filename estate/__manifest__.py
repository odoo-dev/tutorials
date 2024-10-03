{
    "name": "Real_Estate",
    "depends": ["base"],
    "Description": "Estate Module by aneg",
    "category": "Real Estate/Brokerage",
    "license": "LGPL-3",
    "summary": "Real_Estate module for different purpose",
    "author": "aneg_odoo",
    "version": "0.1",
    "application": True,
    "installable": True,
    "data": [
        "security/security.xml",
        "security/ir.model.access.csv",
        "wizard/wizard_views.xml",
        "views/estate_property_views.xml",
        "views/estate_property_offer.xml",
        "views/estate_property_type.xml",
        "views/estate_property_tag.xml",
        "views/estate_menus.xml",
        "views/res_users_view.xml",
        "data/estate.property.type.csv",
        "report/subtemplate_offers_table.xml",
        "report/estate_property_templates.xml",
        "report/estate_property_reports.xml",
        
        
    ],
    "demo": [
        "demo/estate_demo.xml",
        "demo/estate_offer_demo.xml",
    ],
}
