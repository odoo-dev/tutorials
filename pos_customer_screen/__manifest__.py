{
    'name': "POS Customer Screen",
    'version': '1.0',
    'depends': ['pos_restaurant'],
    'author': "Odoo",
    'category': 'Sales/Point of Sale',
    'description': """
    This module
    - Show customer name and amount/guest on ticket screen.
    - Show refunded lines separately subsectioned on customer screen.
    """,
    'assets': {
        'point_of_sale._assets_pos': [
            'pos_customer_screen/static/src/app/models/**/*',
        ],
        'point_of_sale.customer_display_assets': [
            'pos_customer_screen/static/src/customer_display/**/*',
            "pos_customer_screen/static/src/app/generic_components/order_widget/*",
        ],
    },
    'license': 'LGPL-3'
}
