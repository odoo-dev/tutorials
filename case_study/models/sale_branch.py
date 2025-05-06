from odoo import api, fields, models

class SaleBranchModel(models.Model):
    _name = "sale_branch"
    _description = "Sale Branch"

    name = fields.Char(required=True)
    sequence_id = fields.Many2one("ir.sequence")
    code = fields.Char(required=True)

    @api.model_create_multi
    def create(self, val_list):
        for val in val_list:
            sequence_id = self.env['ir.sequence'].create([{
                'name': val["name"],
                'code': val["code"],
            }]).id
            val["sequence_id"] = sequence_id
        return super().create(val_list)
    
    def write(self, values):
        for record in self:
            record.sequence_id.write({
                'name': values['name']
            })
        return super().write(values)
