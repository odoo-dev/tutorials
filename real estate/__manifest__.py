#-*- coding: utf-8 -*-

{
    'name': 'Real Estate',
    'version': '1.0',
    'category': 'Industry/real_estate',
    'description': 'A comprehensive real estate management system that allows management of various real estate properties',
    'summary': 'Real estate',
    'installable': True,
    'application': True,
    'license': 'OEEL-1',
    'depends': ['base'],
    'data':[
        'security/groups.xml',
        'security/ir.model.access.csv',
        'views/estate_property_view.xml',
        'views/estate_property_menus.xml'
        ]
}
