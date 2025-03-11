from odoo import api, fields, models


class ProductTemplate(models.Model):
    _inherit = "product.template"

    has_available_route_ids = fields.Boolean(
        'Routes can be selected on this product', compute='_compute_has_available_route_ids',
        default=lambda self: self.env['stock.route'].search_count(['|', ('product_selectable', '=', True), ('warehouse_selectable', '=', True)]))

    route_ids = fields.Many2many(
        'stock.route', 'stock_route_product', 'product_id', 'route_id', 'Routes',
        domain=['|', ('product_selectable', '=', True), ('warehouse_selectable', '=', True)],
        depends_context=['company', 'allowed_companies'],
        help="Depending on the modules installed, this will allow you to define the route of the product: whether it will be bought, manufactured, replenished on order, etc.",
        compute='_compute_route_ids', store=True, readonly=False)

    available_route_ids = fields.Many2many(
        "stock.route",
        compute="_compute_available_routes",
        store=False
    )

    operations_visibility = fields.Boolean(compute="_compute_operations_visibility")

    def _compute_has_available_route_ids(self):
        self.has_available_route_ids = self.env['stock.route'].search_count(['|', ('product_selectable', '=', True), ('warehouse_selectable', '=', True)])

    def _compute_route_ids(self):
        pass

    def _compute_available_routes(self):
        for product in self:
            product.available_route_ids = self.env["stock.route"].search([('product_selectable', '=', True)])

    @api.depends("available_route_ids")
    def _compute_operations_visibility(self):
        for product in self:
            product.operations_visibility = product.available_route_ids
