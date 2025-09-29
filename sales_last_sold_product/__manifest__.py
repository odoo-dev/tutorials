{
    "name": "Sales - Last sold product",
    "version": "1.0",
    "description": """
        This module displays the last sold (invoiced) products for the selected customer.
        """,
    "category": "Sales/Sales",
    "depends": ["sale_management", "stock"],
    "data": ["views/account_move_views.xml", "views/product_template_views.xml"],
    "installable": True,
    "auto_install": False,
    "license": "LGPL-3",
}
