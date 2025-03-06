{
    'name': 'POS Salesperson Commission',
    'version': '1.0',
    'category': 'Point of Sale',
    'depends': ['point_of_sale'],
    'data': [
        'views/pos_order_views.xml',
        'views/pos_salesperson_commission_view.xml',
        'views/point_of_sale_view.xml',
        'security/ir.model.access.csv',
    ],
    'assets': {
        'point_of_sale._assets_pos': [
            'pos_salesperson_commission/static/src/**/*',
        ],
    },
    'installable': True,
}