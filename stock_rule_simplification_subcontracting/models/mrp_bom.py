from odoo import api, models


class MrpBom(models.Model):
    _inherit = 'mrp.bom'

    @api.model_create_multi
    def create(self, values):
        resupply_route = self.env.ref('mrp_subcontracting.route_resupply_subcontractor_mto', raise_if_not_found=False)

        if resupply_route:
            for value in values:
                if value['type'] == 'subcontract':
                    bom_line_ids = value['bom_line_ids']
                    for bom_line in bom_line_ids:
                        product = self.env['product.product'].browse(bom_line[2]['product_id'])
                        product.product_tmpl_id.route_ids = [(4, resupply_route.id)]

        return super().create(values)

    def write(self, values):
        res = super().write(values)
        resupply_route = self.env.ref('mrp_subcontracting.route_resupply_subcontractor_mto', raise_if_not_found=False)

        if resupply_route:
            for bom in self:
                if bom.type == 'subcontract':
                    bom_line_ids = bom.bom_line_ids
                    for bom_line in bom_line_ids:
                        bom_line.product_id.product_tmpl_id.route_ids = [(4, resupply_route.id)]

        return res

    def unlink(self):
        resupply_route = self.env.ref('mrp_subcontracting.route_resupply_subcontractor_mto', raise_if_not_found=False)

        if resupply_route:
            for bom in self:
                if bom.type == 'subcontract':
                    for bom_line in bom.bom_line_ids:
                        product = bom_line.product_id
                        tmpl = product.product_tmpl_id

                        other_boms = self.search([
                            ('type', '=', 'subcontract'),
                            ('bom_line_ids.product_id', '=', product.id),
                            ('id', '!=', bom.id)
                        ])

                        if not other_boms:
                            tmpl.route_ids = [(3, resupply_route.id)]

        return super().unlink()

