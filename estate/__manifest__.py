{
    'name': 'Real Estate',
    'version': '1.0',
    'category': 'Tutorials',
    'depends': [
        'base'
    ],
    'data': [
        'security/ir.model.access.csv',

        'views/estate_property_views.xml',
        'views/estate_menu_views.xml'
    ],
    'installable': True,
    'application': True,
    'auto_install': False
}
