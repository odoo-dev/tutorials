# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

{
    'name': 'Estate',
    'version': '1.0',
    'category': 'Sales',
    'sequence': 1,
    'summary': 'Tutorial Estate Application',
    'website': 'https://www.odoo.com/app/estate',
    'depends': [
        'base',
    ],
    'data': [
        'security/ir.model.access.csv',

        'views/estate_property_views.xml',
        'views/estate_menus.xml',
    ],
    'installable': True,
    'application': True,
    'author': 'Odoo S.A.',
    'license': 'LGPL-3',
}
