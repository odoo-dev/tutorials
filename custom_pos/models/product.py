from odoo import api, fields, models


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    pos_description = fields.Text(string='POS Description')
    alternative_name = fields.Char(string='Alternative Name')
    pos_alternative_product_ids = fields.Many2many(string="POS Alternative Products",
        comodel_name='product.template',
        relation='pos_product_alternative_rel',
        column1='src_id', column2='dest_id',
        help="Suggest alternative products in the POS product detail popup when 'Point of Sale' is enabled."
    )


class ProductProduct(models.Model):
    _inherit = 'product.product'

    @api.model
    def _load_pos_data_fields(self, config_id):
        result = super()._load_pos_data_fields(config_id)
        result.extend(['pos_description', 'alternative_name', 'pos_alternative_product_ids'])
        return result
