{
    'name': 'Real Estate',
    'version': '1.0',
    'author': 'Abdelrhman Fawzy',
    'category': 'Services/Real Estate',
    'summary': 'Manage real estate properties, offers, and advertisements.',
    'license': 'LGPL-3',
    'application': True,
    'installable': True,
    'auto_install': False,
    'data': [
        'security/ir.model.access.csv',
        'views/estate_property_views.xml',
        'views/estate_property_type_views.xml',
        'views/estate_property_tag_views.xml',
        'views/estate_property_offer_views.xml',
        'views/estate_menues.xml'
    ],
    'description': "This module allows you to manage real estate properties, property types, tags, offers, and advertisements. It also includes tools for organizing and displaying data effectively."
}
