{
    'name': 'Case Study',
    'depends': [
        'sale',
        'account', 
    ],
    'data': [
        'data/ir.model.access.csv',

        'views/sale_branch_views.xml',
        'views/sale_order_views.xml',
        'views/sale_menu_branch.xml',
    ],
    'application': False,
}