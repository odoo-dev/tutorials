from odoo import fields, models


class productTemplate(models.Model):
    _inherit = "product.template"

    require_deposit = fields.Boolean(string="Require Deposit")
    deposit_amount = fields.Float(string="Amount")
