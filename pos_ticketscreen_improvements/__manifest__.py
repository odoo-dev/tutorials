{
    'name': "POS Ticket Screen Improvements",
    'version': '1.0',
    'depends': ['point_of_sale'],
    'author': "Odoo",
    'category': 'Sales/Point of Sale',
    'description': """
    This module enables pos users to pay from ticket screen.
    """,
    'assets': {
        'point_of_sale._assets_pos': [
            'pos_ticketscreen_improvements/static/src/**/*',
        ],
    },
    'license': 'LGPL-3'
}
