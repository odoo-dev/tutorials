{
    "name": "Estate Auction",
    "version": "1.0",
    "description": "Real Estate Automated Auction",
    "summary": "Real Estate Automated Auction",
    "author": "odoo",
    "website": "www.odoo.com",
    "license": "LGPL-3",
    "depends": ["estate"],
    "data": [
        "./views/estate_property_views.xml",
        "./views/estate_property_website_views.xml",
    ],
    'assets': {
        'web.assets_frontend': [
            'estate_auction/static/src/js/**/*'
        ],
    },
    "application": True,
    "installable": True,
}
