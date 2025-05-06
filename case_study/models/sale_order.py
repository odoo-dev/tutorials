from odoo import api, fields, models

class SaleOrderModel(models.Model):
    _inherit = "sale.order"

    branch_id = fields.Many2one("sale_branch", required=True)

    @api.model_create_multi
    def create(self, val_list):
        records = super().create(val_list)
        for record in records:
            record.name = record.branch_id.name + f"-{record.id:04d}"
        return records