{
    "name": "Simplified Receipt",
    "version": "1.0",
    "depends": ["sale_management","point_of_sale","pos_restaurant"],
    'data': [
        'views/res_config_settings_views.xml',
    ],
    'assets': {
        'point_of_sale._assets_pos': [
            'simplified_receipt/static/src/**'
        ],
    },
    "application": True,
    "installable": True,
    "license": "AGPL-3"
}