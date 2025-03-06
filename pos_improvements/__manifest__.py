{
    "name": "POS Improvements",
    "summary": "Allow POS users to pay directly from the ticket screen by loading selected orders onto the payment screen.",
    "description": """ 
        This module enhances the Point of Sale (POS) workflow by adding a "Pay" button to the ticket screen. Users can quickly select an order and load it into the payment screen for seamless transaction processing.

        - Adds a payment button alongside the "Load Orders" button.
        - On clicking, the selected order automatically loads into the payment interface.
        - Improves efficiency by reducing manual steps for cashiers.""",
    "depends": ["point_of_sale"],
    "assets": {
        "point_of_sale._assets_pos": [
            "pos_improvements/static/src/*",
        ],
    },
    "auto_install": True,
    "license": "LGPL-3",
}
