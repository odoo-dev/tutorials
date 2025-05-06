{
    'name': 'Real Estate',
    'depends': [
        'base' 
    ],
    'data': [
        'data/estate_property_type.csv',
        'data/estate_property.xml',
        'data/estate_property_offer.xml',

        'security/ir.model.access.csv',

        'views/estate_property_tag_views.xml',
        'views/estate_property_offer_views.xml',
        'views/estate_property_type_views.xml',
        'views/estate_property_views.xml',
        'views/estate_menus.xml',
        'views/res_users_view.xml'
    ],
    'application': True,
}