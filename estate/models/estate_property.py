from odoo import fields, models


class Estate(models.Model):
    _name = "estate.property"
    _description = "Properties of estate entities."

    buyer = fields.Many2one("res.partner", string="Buyer", copy=False)
    salesperson = fields.Many2one(
            "res.users",
            string="Salesperson",
            default=lambda self: self.env.user)
    active = fields.Boolean(default=True)
    name = fields.Char(string="Name", required=True)
    description = fields.Text()
    property_type_id = fields.Many2one("estate.property.type", string="Type")
    postcode = fields.Char()
    date_availability = fields.Date(
            copy=False,
            default=fields.Date.add(fields.Date.today(), months=3))
    expected_price = fields.Float(required=True, readonly=True, default=99999)
    selling_price = fields.Float(copy=False, readonly=True)
    bedrooms = fields.Integer(default=2)
    living_area = fields.Integer()
    facades = fields.Integer()
    garage = fields.Boolean()
    garden = fields.Boolean()
    garden_area = fields.Integer()
    garden_orientation = fields.Selection(
            string='Orientation',
            selection=[
                ('north', 'North'),
                ('south', 'South'),
                ('east', 'East'),
                ('west', 'West')],
            help="Cardinal orientation of the garden.",
        )
    state = fields.Selection(
            string='State',
            required=True,
            copy=False,
            default='new',
            selection=[('new', 'New'),
                       ('offer received', 'Offer Received'),
                       ('offer accepted', 'Offer Accepted'),
                       ('sold', 'Sold'),
                       ('canceled', 'Canceled')])
