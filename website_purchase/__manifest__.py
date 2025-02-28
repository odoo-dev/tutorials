{
    "name": "Ecommerce for Purchase",
    "version": "1.0",
    "depends": ["website_sale"],
    "description": """
    This is the add-on module that allows users to sell items on e-commerce platform, facilitating purchase for the company.
    """,
    "category": "Website",
    "installable": True,
    "license": "LGPL-3",

    "data": [
        "views/website_purchase_view.xml",
    ],

    'assets': {
        'web.assets_frontend': [
            'website_purchase/static/src/**/*',
        ],
    },
}
