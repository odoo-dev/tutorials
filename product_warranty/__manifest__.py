{
    'name': 'Products Expiration Date',
    'category': 'Inventory/Inventory',
    'depends': ['website_sale_stock'],
    'license': 'LGPL-3',
    'data' : [
        'security/ir.model.access.csv',

        'views/product_views.xml',
        'views/warranty_config_views.xml',
        'views/product_warranty_menu.xml',
        'views/sale_order_views.xml',

        'wizard/choose_warranty_views.xml',
    ],
}
