{
    'name': 'TDS Client',
    'version': '19.0.6.0.0',
    'summary': 'TDS/TCS Validation Client',
    'category': 'Tutorials',
    'author': "Odoo",
    'depends': ['base', 'mail', 'web'],
    'data': [
        'security/ir.model.access.csv',
        'views/tds_client_view.xml',
    ],
    'installable': True,
    'license': 'LGPL-3',
}
