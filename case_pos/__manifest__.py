{
    'name': 'Case Study: POS',
    'summary': 'App for case study: pos',
    'description': 'Sale branch App for case study: pos',
    'license': 'GPL-3',
    'depends': ['point_of_sale'],
    'data': [
        'views/pos_config_views.xml'
    ],
    'assets': {
        'point_of_sale._assets_pos': [
            'case_pos/static/src/**/*',
        ],
    },
    'application': True,
    'installable': True,
}
