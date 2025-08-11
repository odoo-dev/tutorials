# Part of Odoo. See LICENSE file for full copyright and licensing details.

{
    'name': 'Estate',
    'version': '1.0',
    'category': 'Real Estate/Brokerage',
    'sequence': 1,
    'summary': 'Tutorial Estate Application',
    'website': 'https://www.odoo.com/app/estate',
    'depends': [
        'base',
    ],
    'data': [
        'security/ir.model.access.csv',
        'security/estate_security.xml',

        'views/estate_property_offer_views.xml',
        'views/estate_property_type_views.xml',
        'views/estate_property_tag_views.xml',
        'views/estate_property_views.xml',
        'views/inherited_user_views.xml',
        'views/estate_menus.xml',

        'data/estate.property.type.csv',
        'data/estate_property.xml',
        'data/estate_property_offer.xml',

        'report/estate_property_reports.xml',
        'report/estate_property_templates.xml',
        'report/res_users_reports.xml',
        'report/res_users_templates.xml',
    ],
    'installable': True,
    'application': True,
    'author': 'Odoo S.A.',
    'license': 'LGPL-3',
}
