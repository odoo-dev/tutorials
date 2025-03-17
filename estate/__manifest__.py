{
    'name': 'Real Estate',
    'category': 'Real Estate',
    'depends': ['base_setup'],
    'application': True,
    "installable": True,
    'depends':[
        'base_setup'
    ],
    'data': [
        'security/ir.model.access.csv',
        'views/estate_menus.xml',
        'views/estate_property_views.xml'
    ]
}