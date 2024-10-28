{
    'name': "Real Estate",
    'version': '1.0',
    'depends': ['base'],
    'author': "Ayushmaan",
    'category': 'Real Estate/Brokerage',
    'description': """
    First Application
    """,
    # data files always loaded at installation
    'data': [
        "report/estate_property_templates.xml",
        "report/estate_property_reports.xml",
        "report/estate_property_offers_info.xml",
        'security/ir.model.access.csv',
        'security/security.xml',
        "data/estate.property.type.csv",
        'data/demo_data.xml',
        'views/res_users_views.xml',
        'views/estate_property_offer_views.xml',
        'views/estate_property_tag_views.xml',
        'views/estate_property_type_views.xml',
        'views/estate_property_views.xml',
        'views/estate_menus.xml',
        "data/master_data.xml",
    ],
    # data files containing optionally loaded demonstration data
    'demo': [
        # "demo/demo_data.xml",
    ],
    'installable': True,
    'application': True
}
