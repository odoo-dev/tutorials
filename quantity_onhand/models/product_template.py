from odoo import models, fields, api


class ProductTemplate(models.Model):
    _inherit = "product.template"

    is_multi_locations = fields.Boolean(String='Multi Locations', compute="_compute_is_multi_locations", store=True)

    @api.depends('company_id')
    def _compute_is_multi_locations(self):
        for rec in self:
            rec.is_multi_locations = len(self.env.user.company_ids) > 1
