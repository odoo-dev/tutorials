from odoo import api,fields, models

class SaleBranch(models.Model):
    _name = "sale.branch"
    _description = """
    Case Study: Framework Knowledge
    """

    name = fields.Char(required=True)
    sequence_id = fields.Many2one('ir.sequence', 'Reference Sequence')
    code = fields.Char()

    @api.model
    def create(self, vals):
        branch_name, branch_code = vals["name"], vals["code"]
        sequence = self.env['ir.sequence'].create({
            'name': f"Branch Sequence - {branch_name}",
            'prefix': branch_code,
            'padding': 4,
        })
        vals['sequence_id'] = sequence.id

        return super().create(vals)