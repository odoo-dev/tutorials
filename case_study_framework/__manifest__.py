# Part of Odoo. See LICENSE file for full copyright and licensing details.

{
    'name': 'Sales Branches',
    'version': '1.0',
    'category': 'Sales',
    'sequence': 1,
    'summary': 'Tutorial Sales Branch Application',
    'website': 'https://www.odoo.com/app/estate',
    'depends': [
        'base',
        'account',
        'sale_management',
    ],
    'data': [
        'security/ir.model.access.csv',

        'views/inherited_sale_order_views.xml',
        'views/sale_branch_views.xml',
        'views/sale_branch_menus.xml',
    ],
    'installable': True,
    'application': True,
    'author': 'Odoo S.A.',
    'license': 'LGPL-3',
}
