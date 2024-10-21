{
    'name': "Real Estate",
    'version': '0.1',
    'depends': ['base'],
    'author': "Lionel Piraux (lipi)",
    'description': "A real estate app",
    'category': 'Tutorials/RealEstate',
    'application': True,
    'installable': True,
    # data files always loaded at installation
    'data': [
        "security/ir.model.access.csv",
        "views/estate_property_views.xml",
    ],
    # data files containing optionally loaded demonstration data
    'demo': [

    ],
    'license': "LGPL-3",
}
