# case study: point of sale (OWL)
{
    'name': 'ext_casestudy_pos',
    'depends': ['base', 'point_of_sale'],
    'application': False,
    'installable': True,
    'data': [

    ],
    'assets': {
        'point_of_sale._assets_pos': [
            'casestudy_pos/static/src/**/*',
        ]
    }
}