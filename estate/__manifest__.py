# -*- coding: utf-8 -*-
{
    'name': "Real Estate",

    'summary': """
        Estate summary
    """,

    'description': """
        Estate description
    """,

    'depends': ['base'],
    'application': True,
    'installable': True,
    'data': [
        'security/ir.model.access.csv',
        'views/estate_property_views.xml',
        'views/estate_property_tag_views.xml',
        'views/estate_property_offer_views.xml',
        'views/estate_property_type_views.xml',
        'views/res_user_views.xml',
        'views/estate_menus.xml',
    ],
    'demo': [
        'demo/estate.property.type.csv',
        'demo/estate.property.xml',
        'demo/estate.property.offer.xml',
    ]
}
