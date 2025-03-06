# -*- coding: utf-8 -*-

{
    'name': "supplier_portal",
    'author': "Odoo",
    'website': "https://www.yourcompany.com",
    'category': 'Website',
    'version': '1.0',
    'depends': ['base', "account", 'website'],
    'data': [
        'views/templates.xml',
        'views/inherit_views.xml',
    ],
    'assets': {
        'supplier_portal._assets_sop': [
            ('include', 'web._assets_helpers'),
            'web/static/src/scss/pre_variables.scss',
            'web/static/lib/bootstrap/scss/_variables.scss',
            'web/static/lib/bootstrap/scss/_maps.scss',
            ('include', 'web._assets_bootstrap'),
            ('include', 'web._assets_core'),
            'web/static/src/libs/fontawesome/css/font-awesome.css',
            'supplier_portal/static/src/**/*',
        ],
    },
    'application': True,
    'installable': True,
    'license': 'OEEL-1',
}
