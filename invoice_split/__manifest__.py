# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

{
    'name': 'split invoice',
    'summary': 'split invoice',
    'description': "Split invoice by product quantity",
    'category': 'Customization',
    'depends': ['account'],
    'data': [
        'security/ir.model.access.csv',

        'wizard/account_split_wizard.xml',
        'wizard/account_split_move_wizard.xml',

        'views/account_move_views.xml',

    ],
    'installable': True,
    'license': 'LGPL-3',
}
