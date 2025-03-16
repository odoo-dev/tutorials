{
    'name': 'Custom POS',
    'version': '0.1',
    'summary': 'Enhances POS with product descriptions, alternative names, alternative products and real-time stock updates.',
    'description': """
Allows setting a specific description for POS, visible only when set.
Adds a field for an alternative name, searchable and displayed in POS, cart, and receipts.
Enables linking alternative products, showing them in the POS product details.
Displays available quantities on product cards and allows manual syncing.
    """,
    'author': 'Odoo',
    'depends': ['point_of_sale'],
    'data': [
       'views/product_views.xml'
    ],
    'installable': True,
    'auto_install': True,
    'assets': {
        'point_of_sale._assets_pos': [
            'custom_pos/static/src/app/models/*.js',
            'custom_pos/static/src/app/generic_components/**/*',
            'custom_pos/static/src/app/screens/product_screen/**/*',
            'custom_pos/static/src/app/navbar/*',
            'custom_pos/static/src/app/store/**/*'
        ],
        'web.assets_tests': [
            'custom_pos/static/tests/tours/product_screen_tour.js'
        ]
    },
    'license': 'LGPL-3',
}
