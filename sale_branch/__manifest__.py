# -*- coding: utf-8 -*-
{
    'name': "Sale Branch",

    'summary': """
        Sale branch summary
    """,

    'description': """
        Sale branch description
    """,

    'depends': ['base', 'sale'],
    'application': True,
    'installable': True,
    'data': [
        'security/ir.model.access.csv',
        'views/sale_branch_views.xml',
        'views/sale_order_views.xml',
        'views/sale_branch_menu.xml'
    ]
}
