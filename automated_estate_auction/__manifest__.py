{
    "name": "Automated Real Estate Auction",
    "version": "1.0",
    "depends": ["base", "estate", "mail"],
    "description": "Automate auction process to reduce delays",
    "data": [
        "security/ir.model.access.csv",
        "data/estate_property_mail_template.xml",
        "views/estate_property_offer_placed_views.xml",
        "views/estate_property_make_offer_views.xml",
        "views/estate_property_detail_website.xml",
        "views/estate_property_list_website.xml",
        "views/estate_property_views.xml",
    ],
    "sequence": 1,
    "application": True,
    "license": "OEEL-1",
    "installable": True,
}
