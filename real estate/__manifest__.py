#-*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

{
    'name': 'Real Estate',
    'version': '1.0',
    'category': 'Industry/real_estate',
    'description': 'A comprehensive real estate management system that allows management of various real estate properties',
    'summary': 'Real estate',
    'installable': True,
    'application': True,
    'license': 'OEEL-1',
    'depends': ['base', 'website'],
    'data': [
        'security/groups.xml',
        'security/ir.model.access.csv',
        'views/estate_property_offer_view.xml',
        'views/estate_property_model_view.xml',
        'views/estate_property_tags_model_view.xml',
        'views/estate_property_type_model_view.xml',
        'views/estate_property_menus.xml',
        'views/res_user_view.xml',
        'views/template_properties.xml',
        'report/estate_property_report.xml',
        'report/res_user_report.xml'
    ]
}
