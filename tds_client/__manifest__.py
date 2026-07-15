{
    'name': 'TDS Client',
    'version': '19.0.2.0.0',
    'summary': 'TDS/TCS Validation Client — Calls TDS Server API with Webhook Support',
    'category': 'Tutorials',
    'author': 'Odoo',
    'depends': ['base', 'mail', 'web'],
    'data': [
        'security/ir.model.access.csv',
        'data/ir_config_parameter.xml',
        'views/tds_client_views.xml',
    ],
    'installable': True,
    'license': 'LGPL-3',
}
