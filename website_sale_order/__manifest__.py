{
    'name': 'Website Sale Order',
    'category': 'Website/Website',
    'depends': ['website_sale'],
    'version': '1.0',
    'license': 'LGPL-3',
    'data': [
        'views/snippets/s_sale_order.xml',
    ],
    'assets': {
        'web.assets_frontend': [
            'website_sale_order/static/src/snippets/s_sale_order/000.js',
            'website_sale_order/static/src/snippets/s_sale_order/000.xml',
        ],
    }
}
