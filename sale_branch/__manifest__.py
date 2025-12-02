# frtan case study
{
    'name': 'Sales Branch',
    'depends': ['base', 'account', 'sale'],
    'application': False,
    'installable': True,
    'data': [
        'security/ir.model.access.csv',

        'views/sale_branch_views.xml',
        'views/sale_branch_menu.xml',
        'views/sale_order_views.xml',
    ]
}

