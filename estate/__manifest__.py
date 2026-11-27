
{
    'name': 'Real Estate',
    'depends': [
        'base'
    ],
    'category': 'Real Estate/Brokerage',
    'application': True,
    'license': 'LGPL-3',

    'data': [
        'security/estate_security.xml',
        'security/ir.access.csv',
        'views/res_users_views.xml',
        'views/estate_property_offer_views.xml',
        'views/estate_property_views.xml',
        'views/estate_property_type_views.xml',
        'views/estate_property_tag_views.xml',
        'views/estate_menus.xml',
    ],
}
