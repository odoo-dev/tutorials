{
    "name": "POS Pill Display",
    "depends": ["pos_restaurant", "pos_preparation_display"],
    "data": [
        "views/pos_note_view.xml",
    ],
    "assets": {
        "point_of_sale._assets_pos": [
            "pos_pills_display/static/src/app/generic_components/orderline/*",
        ],
        "pos_preparation_display.assets": [
            "pos_pills_display/static/src/app/components/orderline/*",
        ]
    },
    "application": True,
    "license": "LGPL-3",
}
