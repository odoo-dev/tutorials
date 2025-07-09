{
    'name': 'Sales Branches',
    'depends': ['sale_management', 'account'],
    'data': [
        'security/ir.model.access.csv',
        'views/sale_branches_view.xml',
        'views/sale_menu_branches_view.xml',
        'views/sale_order_inherited_view.xml'
    ],
    'license': 'LGPL-3',
}