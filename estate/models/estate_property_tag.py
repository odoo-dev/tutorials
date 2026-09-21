from odoo import fields, models


class EstatePropertyTag(models.Model):
    ## Private attributes ##
    _name = "estate.property.tag"
    _description = "Real estate property tags"
    _order = "name"

    ## Fields declaration ##
    name = fields.Char(required=True)
    color = fields.Integer()

    ## SQL constraints ##
    _name_uniq = models.Constraint(
        "unique(name)",
        "A tag with the same name already exists",
    )
