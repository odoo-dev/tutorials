{
    "name": "POS Pill Improvements",
    "depends": ["pos_restaurant", "point_of_sale"],
    "data": [
        'views/pos_note_view_changes.xml',
    ],
    "assets": {
        "point_of_sale._assets_pos": [
            "pos_pills_improvements/static/src/orderline_pos/*",
        ],
        'pos_preparation_display.assets': [
            "pos_pills_improvements/static/src/orderline_pos_rest/*",
        ]
    },
    "application": True,
    "license": "LGPL-3",
}
