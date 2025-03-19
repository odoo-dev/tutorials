{
    "name": "Combo Choices",
    "version": "1.0",
    "summary": " ",
    "description": """
        ...
    """,
    "depends": ["sale_management", "pos_restaurant"],
    "data": [
        "views/product_combo_views.xml",
    ],
    'assets':{
        'point_of_sale._assets_pos': [
            'combo_choices/static/src/**/*',
        ],
    },
    "installable": True,
    "license": "AGPL-3" 
}