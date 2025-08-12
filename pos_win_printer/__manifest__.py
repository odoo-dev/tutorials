{
    "name": "POS Printer Windows",
    "version": "0.1",
    "author": "Dhruvrajsinh Zala (zadh)",
    "depends": ["point_of_sale"],
    'license': 'LGPL-3',
    "installable": True,
    "assets": {
        "point_of_sale._assets_pos": [
            "pos_win_printer/static/src/overrides/components/pos_store.js"
        ],
    },
}
