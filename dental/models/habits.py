from odoo import fields, models


class DentalHabits(models.Model):
    _name = "habits"
    _description = "This Model is for Medical habits"

    name = fields.Char(required=True)
    sequence = fields.Integer(
        "Sequence",
        default=1,
        help="Used to order stages. Lower is better.",
    )
