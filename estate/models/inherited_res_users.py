from odoo import fields, models


class inheritedResUsers(models.Model):
    _inherit = "res.users"

    property_ids = fields.One2many(
        "estate.property", "salesperson_id", domain=[('state', 'in', ['new', 'offer_recieved'])]
    )