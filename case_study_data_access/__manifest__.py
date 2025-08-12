# Part of Odoo. See LICENSE file for full copyright and licensing details.

{
    'name': 'Sale Data Access',
    'version': '1.0',
    'category': 'Sales',
    'sequence': 1,
    'summary': 'Tutorial Data Access Application',
    'website': 'https://www.odoo.com/app/estate',
    'depends': [
        'sale_management',
    ],
    'data': [
        'security/sales_security.xml',
    ],
    'installable': True,
    'application': True,
    'author': 'Odoo S.A.',
    'license': 'LGPL-3',
}
