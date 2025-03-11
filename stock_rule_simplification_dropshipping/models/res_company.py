from odoo import api, models

class ResCompany(models.Model):
    _inherit = 'res.company'

    @api.model
    def _merge_dropship_rule(self):
        dropship_route = self.env.ref('stock_dropshipping.route_drop_shipping', raise_if_not_found=False)

        subcontracting_route = self.env.ref('mrp_subcontracting_dropshipping.route_subcontracting_dropshipping', raise_if_not_found=False)
        subcontracting_rules = self.env['stock.rule'].search([('route_id', '=', subcontracting_route.id)])

        for sr in subcontracting_rules:
            sr.update({"route_id": dropship_route.id})

        subcontracting_route.active = False

        self.env.company.dropship_subcontractor_pick_type_id.active = False
