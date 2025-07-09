{
    'name': 'Real Estate',
    'depends': ['base'],
    'data': [
        'security/ir.model.access.csv',

        'views/estate_property_offer_views.xml',
        'views/estate_property_type_views.xml',
        'views/estate_property_tag_views.xml',
        'views/estate_property_views.xml',
        'views/estate_menus.xml',
        'views/res_users_views.xml',

        'report/estate_property_reports.xml',
        'report/estate_property_templates.xml',
        'report/ref_users_reports.xml',
        'report/ref_users_templates.xml',

        'data/estate.property.type.csv',
        'data/estate.property.xml',
        'data/estate.property.offers.xml',

    ],
    'application': True,
    'license': 'LGPL-3',
}