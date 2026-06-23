{
    'name': 'Add Product Type',
    'author': "keman",
    'license': 'LGPL-3',
    'depends': ["sale", "product"],
    'data': [
        'security/ir.model.access.csv',
        'views/product_template_views.xml',
        'views/sale_order_views.xml',
        'wizard/product_kit_wizard_views.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'new_product_type/static/src/js/product_kit_sale_order_line.js',
        ],
    },
}
