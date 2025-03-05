# -*- coding: utf-8 -*-

{
    'name': "sale_order_book_price",
    'author': "Odoo",
    'website': "https://www.odoo.com/odoo/order",
    'category': 'Sales',
    'version': '1.0',
    'depends': ['sale_management', 'account'],
    'data': [
        'views/account_move_inherited_views.xml',
        'views/sol_inherited_views.xml',
    ],
}
