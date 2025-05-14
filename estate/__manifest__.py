{
    'name': 'Real Estate',
    'category': 'Real Estate/Brokerage',
    'depends': [
        'base' 
    ],
    'data': [
        'data/estate_property_type.csv',
        'data/estate_property.xml',
        'data/estate_property_offer.xml',

        'report/estate_property_template.xml',
        'report/res_users_template.xml',
        'report/estate_property_report.xml',
        'report/res_users_report.xml',

        'security/ir.model.access.csv',
        'security/security.xml',

        'views/estate_property_tag_views.xml',
        'views/estate_property_offer_views.xml',
        'views/estate_property_type_views.xml',
        'views/estate_property_views.xml',
        'views/estate_menus.xml',
        'views/res_users_view.xml'
    ],
    'application': True,
}