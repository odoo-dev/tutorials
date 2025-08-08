# Part of Odoo. See LICENSE file for full copyright and licensing details.

{
    'name': 'Case Study Report',
    'version': '1.0',
    'category': 'Sales',
    'sequence': 1,
    'summary': 'Tutorial Report Application',
    'website': 'https://www.odoo.com/app/estate',
    'depends': [
        'base',
        'account',
        'contacts',
    ],
    'data': [
        'report/res_partner_templates.xml',
        'report/res_partner_reports.xml',
        'report/account_move_templates.xml',
    ],
    'installable': True,
    'application': True,
    'author': 'Odoo S.A.',
    'license': 'LGPL-3',
}
