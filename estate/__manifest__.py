{
    'name': 'Real Estate',
    'summary': 'Estate summary',
    'description': 'Estate description',
    'license': 'GPL-3',
    'depends': ['base'],
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
        'demo/estate.property.type_demo.csv',
        'demo/estate.property_demo.xml',
        'demo/estate.property.offer_demo.xml',
    ],
    'application': True,
    'installable': True,
}
