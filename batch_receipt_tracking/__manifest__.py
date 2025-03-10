# -*- coding: utf-8 -*-
{
    'name': "batch_receipt_tracking",
    'author': "Odoo",
    'website': "https://www.yourcompany.com",
    'category': 'Inventory',
    'version': '1.0',
    'depends': ['purchase' ,'stock'],
    'data': [
        'security/ir.model.access.csv',
        'views/stock_picking_inherit_views.xml',
        'views/res_config_settings_views.xml',
        'views/product_inherit_views.xml',
    ],
    'license': 'LGPL-3',
}

