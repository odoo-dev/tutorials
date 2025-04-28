{
    'name': "Custom Image",
    'category': 'Website/Custom Image',
    'installable': True,
    'license': 'LGPL-3',
    'depends': ['sale_management', 'website_sale'],
    'data': [
        "views/product_views.xml",
        "views/sale_order_views.xml",
        "views/templates.xml",
    ],
    'assets': {
        'web.assets_frontend': [
            'custom_image/static/src/js/website_sale.js',
            'custom_image/static/src/js/product_configurator_dialog.js',
        ]
    }
}
