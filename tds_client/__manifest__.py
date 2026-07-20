{
    'name': 'TDS Client',
    'version': '1.0',
    'summary': 'TDS/TCS Validation Client - Calls TDS Server API',
    'category': 'Tutorials',
    'author': "Odoo",
    'depends': ['base', 'mail'],
    'data': [
        'security/ir.model.access.csv',
        'views/tds_client_view.xml',
    ],
    'installable': True,
    'license': 'LGPL-3',
}
