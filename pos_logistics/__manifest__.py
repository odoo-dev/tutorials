{
    'name': 'pos_logistics',
    'version': '1.0',
    'description': 'to add logistic information into POS products',
    'summary': '',
    'author': 'ERLE',
    'website': '',
    'license': 'LGPL-3',
    'category': '',
    'depends': [
        'point_of_sale',
    ],
    "data": [
        "views/pos_config_views.xml",
    ],
    'assets': {
        'point_of_sale._assets_pos': [
            'pos_logistics/static/src/**/*',
        ],
    },
    'auto_install': True,
    'application': False,
}
