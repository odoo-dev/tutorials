{
    'name': 'Purchase Product Configurator',
    'summary': 'Add variants in purchase order through purchase product configurator',
    'website': 'https://www.odoo.com/app/purchase',
    'category': 'Inventory/Purchase',
    'version': '0.1',
    'depends': ['sale_purchase'],
    'data': [
        'views/purchase_views.xml',
        'views/res_config_settings_views.xml',
    ],
    'installable': True,
    'assets': {
        'web.assets_backend': [
            'purchase_product_configurator/static/src/js/purchase_product_field.js',
            'purchase_product_configurator/static/src/js/purchase_product_configurator_dialog.js',
            'purchase_product_configurator/static/src/js/purchase_product_field.xml',
        ],
        'web.assets_unit_tests': [
            'purchase_product_configurator/static/tests/*',
        ],
    },
    'license': 'LGPL-3',
}
