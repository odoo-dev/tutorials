from odoo import fields, models


class AccountMove(models.Model):
    ## Private attributes ##
    _inherit = "account.move"

    ## Fields declaration ##
    property_id = fields.Many2one("estate.property")
