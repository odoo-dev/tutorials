from odoo import api, fields, models


class SubscriptionPricingRules(models.Model):
    _name = "sale.subscription.pricing"
    _inherit = ["sale.subscription.pricing","product.pricelist.item"]
    
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
        records = super().create(vals_list) 
        for record in records:
            record.product_id = record.product_template_id.id
            
        return records
