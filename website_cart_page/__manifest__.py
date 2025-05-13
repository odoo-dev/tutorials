{
    'name': 'Website Cart Image Upload',
    'version': '1.0',
    'description': """
        This module allows users to upload a custom image on the website product page,
        and saves it on the corresponding product template.
    """,
    'author': 'Rishav Shah',
    'category': 'Website',
    'license': 'LGPL-3',
    'depends': ['website_sale', 'sale_management'],
    'data': [
        'security/ir.model.access.csv',
        'security/sale_order_line_security.xml',
        'views/product_views.xml',
        'views/template.xml',
        'views/sale_order_views.xml',
    ],
    'assets': {
        'web.assets_frontend': [
            'website_cart_page/static/src/js/website_sale.js',
        ]
    },
    'installable': True,
    'application': False,
}
