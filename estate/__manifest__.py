{
    "name": "Real Estate",
    "description": "An app where you can list and buy real estate listings.",
    "depends": ["base"],
    "application": True,
    "author": "Ziad El-Gafy (ziel)",
    "license": "LGPL-3",
    "data": [
        "security/ir.model.access.csv",
        "views/estate_property_views.xml",
        "views/estate_property_offer_views.xml",
        "views/estate_property_type_views.xml",
        "views/estate_property_tag_views.xml",
        "views/estate_menus.xml",
        "views/res_users_views.xml",
    ],
}
