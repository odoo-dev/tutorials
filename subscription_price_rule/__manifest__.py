{
    'name': 'Price Rules For Subscription',
    'version': '1.0',
    'license': 'LGPL-3',    
    'depends': [
        'sale_renting','sale_management','sale_subscription',
    ],
    'data': [
        'views/product_views.xml',
        "views/subscription_pricing_rules_views.xml",
        'views/product_pricelist_view.xml',
        'views/product_pricelist_item_views.xml',
    ],
}
