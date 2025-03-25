from odoo import api, fields, models


class Product(models.Model):
    _inherit = 'product.template'

    is_multi_location_enabled = fields.Boolean(
        string="Multi-Location Enabled",
        compute='_compute_is_multi_location_enabled',
        store=False
    )

    @api.depends_context('uid')
    def _compute_is_multi_location_enabled(self):
        for record in self:
            record.is_multi_location_enabled = self.env.user.has_group('stock.group_stock_multi_locations')

    @api.onchange('qty_available')
    def change_product_qty(self):
        """ Changes the Product Quantity by creating/editing corresponding quant.
        """
        warehouse = self.env['stock.warehouse'].search(
            [('company_id', '=', self.env.company.id)], limit=1
        )
        # Before creating a new quant, the quand `create` method will check if
        # it exists already. If it does, it'll edit its `inventory_quantity`
        # instead of create a new one.
        self.env['stock.quant'].with_context(inventory_mode=True).create({
            'product_id': self.product_variant_id.id,
            'location_id': warehouse.lot_stock_id.id,
            'inventory_quantity': self.qty_available,
        })._apply_inventory()
        return {'type': 'ir.actions.act_window_close'}
