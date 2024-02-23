{
    'name' : "Real Estate",
    'version' : "1.0",
    'category': "estate",
    'summary' : "The Real Estate Advertisement module",
    'depends': ['base'],
    'installable' : True,
    'application' : True,
    'license' : "LGPL-3",
    'data': [
        'security/ir.model.access.csv',
        'views/estate_property_offer_views.xml',
        'views/estate_property_type_views.xml',
        'views/estate_property_tags_views.xml',
        'views/estate_property_views.xml',
        'views/res_users_views.xml',
        'views/estate_menus.xml',
        'report/estate_property_templates.xml',
        'report/estate_property_reports.xml'
    ]
}
