{
    'name': 'Sale Branch',
    'summary': 'Sale branch summary',
    'description': 'Sale branch description',
    'license': 'GPL-3',
    'depends': ['base', 'sale'],
    'data': [
        'security/ir.model.access.csv',
        'views/sale_branch_views.xml',
        'views/sale_order_views.xml',
        'views/sale_branch_menu.xml'
    ],
    'application': True,
    'installable': True,
}
