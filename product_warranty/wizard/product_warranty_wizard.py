from odoo import api, Command, fields, models

class ProductWarrantyWizard(models.TransientModel):
    _name = 'product.warranty.wizard'
    _description = 'To configure warranty for products'

    order_id = fields.Many2one('sale.order', default=lambda self: self.env.context.get('active_id'), ondelete='cascade')
    allowed_product_ids = fields.One2many('product.product', compute='_compute_available_products')
    wizard_line_ids = fields.One2many(
        comodel_name='product.warranty.wizard.line',
        inverse_name='wizard_id',
        compute='_compute_wizard_line_ids',
    )

    @api.depends('allowed_product_ids')
    def _compute_wizard_line_ids(self):
        for wizard in self:
            wizard_line_list = []
            wizard.allowed_product_ids = wizard.order_id.order_line.filtered(
                lambda line: line.product_id.is_warranty_available
            ).mapped('product_id')
            for product in self.allowed_product_ids:
                wizard_line_list.append({
                    'product_id': product.id,
                })
            wizard.wizard_line_ids = [Command.clear()] + [
                Command.create(vals)
                for vals in wizard_line_list
            ]

    @api.depends('order_id')
    def _compute_available_products(self):
        for wizard in self:
            wizard.allowed_product_ids = wizard.order_id.order_line.filtered(
                lambda line: line.product_id.is_warranty_available
            ).mapped('product_id')

    def action_add_warranty(self):
        pass

class ProductWarrantyWizardLine(models.TransientModel):
    _name = 'product.warranty.wizard.line'
    _description = "To configure each product's warranty"

    wizard_id = fields.Many2one('product.warranty.wizard', required=True, ondelete='cascade')
    product_id = fields.Many2one('product.product', string="Product")
    warranty_id = fields.Many2one('product.warranty', string="Warranty")
    # end_date = fields.Date(compute='_compute_end_date')

    @api.depends('warranty_id')
    def _compute_end_date(self):
        pass
