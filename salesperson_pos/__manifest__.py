{
    'name': 'salesperson_pos',
    'description': 'An extension module for point_of_sale in which we can select the salesperson in the order screen for the particular order',
    'version': '1.0',
    'author': 'Vedant Pandey (vpan)',
    'depends': ['point_of_sale', 'hr'],
    'data': [
        "views/pos_order_views.xml",
    ],
    'assets': {
        "point_of_sale._assets_pos":[
            'salesperson_pos/static/src/app/screens/product_screen/control_button/**/*',
            'salesperson_pos/static/src/app/models/pos_order.js'
        ]
    },
    'license': 'LGPL-3',
    'installable': True,
}
