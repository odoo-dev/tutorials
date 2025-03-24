{
    "name": "Last Sold Products",
    "description": "Show last sold products for a customer",
    "depends": ["sale_management", "account", "purchase", "stock"],
    "data": [
        "views/account_move_form.xml",
        "views/sale_order_form.xml",
        "views/purchase_order_form.xml",
        "views/product_view_kanban_catalog.xml",
    ],
    "installable": True,
    "application": False,
    "license": "LGPL-3",
    "assets": {
        "web.assets_backend": [
            "last_sold_products/static/src/css/style.css",
            "last_sold_products/static/src/js/product_catalog.js",
            "last_sold_products/static/src/js/kanban_model.js",
            "last_sold_products/static/src/autocomplete/autocomplete.xml",
        ],
    },
}
