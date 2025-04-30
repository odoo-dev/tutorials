from odoo import fields, models


class InheritedUser(models.Model):
    _inherit = "res.users"

    property_ids = fields.One2many(
        "estate_property",
        "salesperson_id",
        string="Real Estate Properties",
        domain=['|', ('state', '=', 'new'), ('state', '=', 'offer_received')],
    )
