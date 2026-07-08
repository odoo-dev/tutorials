{
    'name': 'TDS Validation',
    'version': '19.0.1.0.0',
    'summary': 'Run TDS FVU validation from Odoo via CLI',
    'category': 'Tutorials',
    'depends': ['base', 'mail'],
    'data': [
        'security/ir.model.access.csv',
        'views/tds_validation_views.xml',
    ],
    'installable': True,
    'license': 'LGPL-3',
}
