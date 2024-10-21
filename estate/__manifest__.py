{
    'name': "Estate",
    'version': '1.0',
    'depends': ['base'],
    'author': "cove",
    'license': "LGPL-3",
    'category': 'Category',
    'application': True,
    'description': """
    Tutorial app - Estate module 
    """,
    # data files always loaded at installation
    'data': [
        'views/estate_property_view.xml',
        'views/estate_property_type_view.xml',
        'views/estate_property_offer_view.xml',
        'views/estate_menus.xml',
        'security/ir.model.access.csv',
    ],
    # data files containing optionally loaded demonstration data
    'demo': [
    ],
}