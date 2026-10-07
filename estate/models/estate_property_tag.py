from odoo import fields, models


class EstatePropertyTag(models.Model):
    _name = "estate.property.tag"
    _description = "Different Tags for Property"

    name = fields.Char("Tag")
    _check_tag_name = models.Constraint("unique(name)", "Tag name should be unique")
