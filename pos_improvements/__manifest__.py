{
    "name": "POS Improvements",
    "version": "1.0",
    "depends": ["sale_management","point_of_sale"],
    "application": True,
    "installable": True,
    'assets': {
         'point_of_sale._assets_pos': [
            'pos_improvements/static/src/ticket_screen/**/*',
         ]
    },
    "license": "AGPL-3"
}