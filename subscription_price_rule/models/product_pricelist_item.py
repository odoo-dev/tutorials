from odoo import models, fields


class ProductPriceListItem(models.Model):
    _inherit = 'product.pricelist.item'

    compute_price = fields.Selection(
        selection=[
            ('percentage', "Discount"),
            ('formula', "Formula"),
            ('fixed', "Fixed Price"),
        ],
        help="Use the discount rules and activate the discount settings"
                " in order to show discount to customer.",
        index=True, default='percentage', required=True)
