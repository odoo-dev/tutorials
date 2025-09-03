from odoo import api, fields, models


class InheritedUsers(models.Model):
    _inherit = "res.users"

    property_ids = fields.One2many(
        "estate.property",
        "salesperson_id",
        string="Properties",
        domain=[("active", "=", True)],
    )
