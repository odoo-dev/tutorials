# -*- coding: utf-8 -*-
{
    'name': 'test-estate',
    'application': True,
    'installable': True,
    'depends': ['base'],
    'data': [
        'security/ir.model.access.csv',

        'views/estate_property_views.xml',
        'views/estate_property_menu_views.xml',
        ],
    'license': 'AGPL-3'
}