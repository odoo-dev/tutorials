{
    'name': 'Sale Branch',
    'version': '0.1',
    'description': 'Tutorial: branch-based quotation naming',
    'summary': '',
    'author': 'ERLE',
    'license': 'LGPL-3',
    'category': 'Sale',
    'depends': [
        'sale_management'
    ],
    'data': [
        'security/ir.model.access.csv',
        'views/sale_branch_views.xml',
        'views/sale_order_views_inherit.xml',
    ],
    'auto_install': False,
    'application': False,
}
