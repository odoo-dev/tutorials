{
    'name': "estate",
    'version': '1.0',
    'depends': ['base', 'mail'],
    'author': "jeep-odoo",
    'category': 'estate',
    'application': True,
    'installable': True,
    'data': [
        'security/ir.model.access.csv',
        'views/estate_property_views.xml',
        'views/estate_menus.xml',
    ],
}
