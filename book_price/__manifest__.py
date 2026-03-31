{
    'name': 'Book Price in Sales & Invoice',
    'version': '1.0',
    'depends': ['sale', 'account'],
    'data': [
        "views/sale_order_views.xml",
        "views/account_move_views.xml",
    ],
    'auto_install': True,
    "author": "assri",
    "license": "LGPL-3",
}
