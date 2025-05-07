from odoo import api, fields, models

class SaleOrderModel(models.Model):
    _inherit = "sale.order"

    branch_id = fields.Many2one("sale_branch", required=True)

    @api.model_create_multi
    def create(self, val_list):
        records = super().create(val_list)
        for record in records:
            seq_code = record.branch_id.sequence_id.code
            seq_name = record.branch_id.sequence_id.next_by_code(seq_code)
            record.name = seq_name
        return records