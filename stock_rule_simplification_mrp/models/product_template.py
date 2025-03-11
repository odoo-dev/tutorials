from odoo import api, models


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    @api.depends('bom_ids')
    def _compute_route_ids(self):
        manufacture_boms = self.bom_ids.filtered(lambda l: l.type == 'normal')
        manufacture_route = self.env.ref('mrp.route_warehouse0_manufacture', raise_if_not_found=False)
        if manufacture_route:
            if len(manufacture_boms.ids) > 0:
                    self.route_ids = [(4, manufacture_route.id)]
            else:
                self.route_ids = [(3, manufacture_route.id)]

        return super()._compute_route_ids()
