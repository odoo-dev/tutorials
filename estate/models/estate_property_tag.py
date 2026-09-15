from odoo import models, fields


class EstatePropertyTag(models.Model):
    # Private attributes
    _name = "estate.property.tag"
    _description = "Tag for estate property"
    _order = "name"

    # Field declarations
    name = fields.Char(required=True)
    tag_color = fields.Integer()

    # SQL constraints and indexes
    _unique_name = models.UniqueIndex(
        "(name)", "Tag with the same name already exists."
    )
