{
    'name': 'Price Rules For Rental',
    'version': '1.0',
    'license': 'LGPL-3',
    'depends': [
        'sale_renting','sale_management','sale_subscription','product'
    ],
    'data': [
        "views/product_views.xml",
        "views/rental_pricing_rules_views.xml",
        'views/product_pricelist_views.xml',
    ],
}

# product.pricelist.form.inherit.sale_renting
# def _compute_price_unit(self): sale
    # -> def _get_display_price(self): sale
        # ->  def _get_display_price_ignore_combo(self) sale
            # -> def _get_pricelist_price(self): sale
                # -> def _get_pricelist_price(self): "sale_renting model"
                    # -> def _get_product_price(self, product, *args, **kwargs): "product module"
                        # -> def _compute_price_rule(
                                #     self, products, quantity, currency=None, date=False, start_date=None, end_date=None,
                                #     **kwargs
                                # ): "sale_renting module"

                                    # -> def _get_best_pricing_rule() "product.template model inside sale renting module"



# sale order line have pricelist_item_id field
    # it has a compute method _compute_pricelist_item_id 
        # It uses a _get_product_rule method to get a price rule according to the quantity of the product
            # then it call _compute_price_rule  
                # Inside is applicable for i need to pass the converted into hours and in the price list i need to compute the min_quantity based on the set unit like day if day then * by 24hours and if week then * by 168
                    # qty_in_product_uom = it is my quantity which is in the sale order line But here i need to pass the converted hours


    # So to complete this:
        # Task 1: store the min_quantity in hours 
        # Task 2: Extend sale order line method to pass a quantity on the based of duration


# Need to override two functions
# 1. _compute_base_price => product.pricelist.item
# 2. _compute_price => product.pricelist.item
