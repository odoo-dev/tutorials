{
    'name': 'TDS Validation',
    'version': '19.0.3.0.0',
    'summary': 'TDS FVU Validation',
    'category': 'Tutorials',
    'author': 'Odoo',
    'depends': ['base', 'mail', 'web'],
    'data': [
        'security/ir.model.access.csv',
        'views/tds_validation_views.xml',

    ],
    'installable': True,
    'license': 'LGPL-3',
}
