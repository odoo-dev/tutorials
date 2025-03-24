from odoo import api, fields, models
from odoo.exceptions import UserError


class SubscriptionPricingRules(models.Model):
    _name = "sale.subscription.pricing"
    _inherit = ["sale.subscription.pricing","product.pricelist.item"]
    
    period_unit = fields.Char(related="plan_id.billing_period_display")
    compute_price = fields.Selection(
        selection=[
            ('percentage', "Discount"),
            ('formula', "Formula"),
            ('fixed', "Fixed Price"),
        ],
        help="Use the discount rules and activate the discount settings"
                " in order to show discount to customer.",
        index=True, default='percentage', required=True)

    
    @api.model_create_multi
    def create(self, vals_list):
        records = self.env[self._name]
        Product = self.env['product.product']
        Category = self.env['product.category']
        
        for vals in vals_list:
            vals_copy = vals.copy()
            display_on = vals.get('display_applied_on')
            categ_id = vals.get('categ_id')
            product_tmpl_id = vals.get('product_tmpl_id')
            
            if display_on == '2_product_category' and categ_id:
                category = Category.browse(categ_id)
                if not category.exists():
                    raise UserError("Selected category does not exist.")
                
                products = Product.search([
                    ('categ_id', '=', category.id),
                    ('recurring_invoice', '=', True)
                ])
            elif display_on == '1_product' and product_tmpl_id:
                products = Product.search([
                    ('product_tmpl_id', '=', product_tmpl_id),
                    ('recurring_invoice', '=', True)
                ], limit=1)
            elif display_on == '1_product':
                products = Product.search([
                    ('recurring_invoice', '=', True)
                ])
            else:
                raise UserError("You cannot create a subscription-based rule for a non-subscribable category.")
            
            if not products:
                raise UserError("You cannot create a subscription-based rule for non-subscribable products.")
            
            for product in products:
                vals_copy.update({
                    'product_id': product.id,
                    'product_template_id': product.product_tmpl_id.id,
                    'product_tmpl_id': product.product_tmpl_id.id
                })
                records += super().create([vals_copy])
        
        return records
            
            
        @api.onchange('product_template_id')
        def _onchange_(self):
            self.product_tmpl_id = self.product_template_id
        