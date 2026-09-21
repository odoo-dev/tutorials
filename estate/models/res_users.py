from odoo import fields, models


class ResUsers(models.Model):
    ## Private attributes ##
    _inherit = "res.users"

    ## Fields declaration ##
    property_ids = fields.One2many(
        "estate.property",
        inverse_name="salesperson_id",
        domain=["|", ("state", "=", "new"), ("state", "=", "offer_received")],
    )
