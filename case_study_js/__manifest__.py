# Part of Odoo. See LICENSE file for full copyright and licensing details.

{
    'name': 'Case Study JS',
    'version': '1.0',
    'category': 'Sales',
    'sequence': 1,
    'summary': 'Tutorial JS Application',
    'website': 'https://www.odoo.com/app/estate',
    'depends': [
        'base',
        'point_of_sale'
    ],
    'data': [
        'views/inherited_pos_config_views.xml'
    ],
    'assets': {
        'point_of_sale._assets_pos': [
            'case_study_js/static/src/**/*',
        ],
    },
    'installable': True,
    'application': True,
    'author': 'Odoo S.A.',
    'license': 'LGPL-3',
}
