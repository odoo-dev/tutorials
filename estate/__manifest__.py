# 19.0-tutorial-frtan
{
    'name': "Estate",
    'depends': ['base'],
    'application': True,
    'installable': True,
    'data': [
        'security/ir.model.access.csv',

        'views/estate_property_offer_views.xml',
        'views/estate_property_views.xml',
        'views/estate_property_type_views.xml',
        'views/estate_property_tag_views.xml',
        'views/estate_menus.xml',
        'views/res_user_views.xml',

        'data/estate.property.type.csv',

        'report/estate_property_reports.xml',
        'report/estate_property_templates.xml',
        'report/res_users_reports.xml',
        'report/res_users_templates.xml'
    ],
    'demo': [
        'demo/estate.property.xml',
        'demo/estate.property.offer.xml'
    ]
}