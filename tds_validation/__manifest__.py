{
    'name': 'TDS Validation',
    'version': '19.0.7.0.0',
    'summary': 'TDS FVU Validation',
    'category': 'Tutorials',
    'author': 'Odoo',
    'depends': ['base', 'mail', 'web'],
    'data': [
        'security/ir.model.access.csv',
        'data/ir_config_parameter.xml',
        'data/ir_cron.xml',
        'views/tds_validation_views.xml',
    ],
    'installable': True,
    'license': 'LGPL-3',
}
