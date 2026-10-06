from odoo import fields, models


class EstateProperty(models.Model):
    _name = "estate.property"
    _description = "Real Estate Property"

    name = fields.Char(required=True)
    description = fields.Text()
    postcode = fields.Char(required=True)
    date_availability = fields.Date()
    expected_price = fields.Float(required=True)
    bedrooms = fields.Integer()
    living_area = fields.Integer()
    facades = fields.Integer()
    garage = fields.Boolean()
    garden = fields.Boolean()
    garden_area = fields.Integer()
    selling_price = fields.Float()
    garden_orientation = fields.Selection(
        selection=[
            ("north", "North"),
            ("south", "South"),
            ("east", "East"),
            ("west", "West"),
        ],
        copy=False,
    )
    active = fields.Boolean(default=True)
    state = fields.Selection(
        selection=[
            ("new", "New"),
            ("offer_received", "Offer Received"),
        ],
        copy=False,
    )
    buyer = fields.Many2one("res.partner", copy=False)
    salesperson = fields.Many2one("res.users", default=lambda self: self.env.user)
    property_type_id = fields.Many2one("estate.property.type", string="Property Type")
    property_tag_ids = fields.Many2many(
        "estate.property.tag",
        column1="estate_property_id",
        column2="estate_property_tag_id",
    )
    offer_ids = fields.One2many(
        "estate.property.offer",
        "property_id",
        string="Offers",
    )
