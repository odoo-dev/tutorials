# Part of Odoo. See LICENSE file for full copyright and licensing details.
{
    "name": "estate",
    "version": "1.0",
    "summary": "real estate",
    "depends": [
        "base_setup",
    ],
    "category": "Real Estate/Brokerage",
    "data": [
        "security/estate_groups.xml",
        "security/ir.model.access.csv",
        "security/estate_security.xml",

        "views/estate_property_offer_views.xml",
        "views/estate_property_tag_views.xml",
        "views/estate_property_type_views.xml",
        "views/estate_property_views.xml",
        "views/estate_menus.xml",
        "views/res_users_view.xml",

        "data/estate.property.type.csv",
        "data/estate_data.xml",
        "data/estate_offer_data.xml",

        "report/estate_property_template.xml",
        "report/users_estate_property_template.xml",
        "report/estate_property_report.xml",
    ],
    "license": "LGPL-3",
}
