# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

{
    "name": "Real Estate",
    "category": "Real Estate/Brokerage",
    "depends": [
        "base",
    ],
    "data": [
        "security/ir.model.access.csv",
        "security/security.xml",
        "views/estate_property_views.xml",
        "views/estate_menus.xml",
        "views/estate_property_tag_views.xml",
        "views/estate_property_type_views.xml",
        "views/estate_property_offer_views.xml",
        "views/inherited_user_views.xml",
        "data/estate.property.type.csv",
        "data/estate.property.offer.xml",
        "data/estate.property.xml",
        "report/estate_report_views.xml",
        "report/estate_reports.xml",
        "report/estate_templates.xml",
        "report/user_reports.xml",
    ],
    "application": True,
    "installable": True,
}
