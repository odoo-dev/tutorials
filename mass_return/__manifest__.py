{
    'name': 'Mass Return',
    'description': """
        This custom module provides functionality to mass return delivered products
    """,
    'depends': ['account', 'sale_management', 'stock', 'purchase'],
    'author': 'Dhruv Godhani',
    'installable': True,
    'data': [
        "views/stock_picking_return_views.xml",
        "views/stock_picking_views.xml",
    ],
    'license': 'LGPL-3',

}
