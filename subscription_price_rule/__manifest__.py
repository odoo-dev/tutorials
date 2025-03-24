{
    'name': 'Price Rules For Subscription',
    'version': '1.0',
    'depends': [
        'product','sale_subscription','sale_renting','sale_management'
    ],
    'data': [
        'views/product_views.xml',
        "views/subscription_pricing_rules_views.xml",
        'views/product_pricelist_view.xml',
    ],
}

# product_pricelist_item_form_view : wizard view ID
