{
    'name': 'estate',
    'version': '1.0',
    'summary': 'A real estate management application',
    'description': 'A module for managing real estate properties, offers, and related entities.',
    'category': 'Real Estate/Brokerage',
    'author': 'YASP',
    'website': 'https://www.yaspestate.com',
    'sequence': 1,
    'depends': ['base', 'website'],
    'license': 'LGPL-3',
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'data/data.xml',
        'report/estate_property_offer_template.xml',
        'report/estate_property_template.xml',
        'report/estate_property_report.xml',
        'wizard/estate_add_offer_wizard_views.xml',
        'data/estate_property_type_data.xml',
        'views/estate_property_views.xml',
        'views/estate_property_offers_views.xml',
        'views/estate_property_types_views.xml',
        'views/estate_property_tags_views.xml',
        'views/estate_property_website_templates_views.xml',
        'views/res_users_views.xml',
        'views/estate_menus.xml'
    ],
    'demo': [
        'demo/estate_property_demo.xml'
    ],
    'installable': True,
    'application': True,
}
