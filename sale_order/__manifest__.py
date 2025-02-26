# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

{
    'name': 'Sale Order Price Divider',
    'version': '1.0',
    'category': 'Sales',
    'summary': 'Wizard to divide sale order price and assign to a buyer',
    'depends': ['sale_management'],
    'data': [
        'views/sale_order_wizard_views.xml',
        'views/sale_order_inherit_views.xml',
        'security/ir.model.access.csv',
    ],
    'installable': True,
    'application': False,
    'license': 'AGPL-3',
}
