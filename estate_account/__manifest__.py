# Part of Odoo. See LICENSE file for full copyright and licensing details.

{
    'name': 'Estate Account',
    'version': '1.0',
    'category': 'Sales',
    'sequence': 1,
    'summary': 'Tutorial Estate Account Application',
    'website': 'https://www.odoo.com/app/estate',
    'depends': [
        'base',
        'estate',
        'account',
    ],
    'data': [
        'report/estate_account_templates.xml',
    ],
    'installable': True,
    'application': True,
    'author': 'Odoo S.A.',
    'license': 'LGPL-3',
}
