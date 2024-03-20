from dateutil.relativedelta import relativedelta
from odoo import fields, models, api


class EstateProperty(models.Model):
    _name = "estate.property"
    _description = "A property managed by the Estate module."

    name = fields.Char(required=True)
    description = fields.Text()
    postcode = fields.Char()
    date_availability = fields.Date(copy=False, default= fields.Date.today()+relativedelta(months=3))
    expected_price = fields.Float(required=True)
    selling_price = fields.Float(readonly=True, copy=False)

    bedrooms = fields.Integer(default=2)
    living_area = fields.Integer()
    facades = fields.Integer()

    active = fields.Boolean(default=True)
    state = fields.Char()

    garage = fields.Boolean()
    garden = fields.Boolean()
    garden_area= fields.Integer()
    garden_orientation = fields.Selection(
        selection=[("north", "North"), ("south", "South"), ("east", "East"), ("west", "West")]
    )
    state = fields.Selection(
        selection=[("new", "New"), ("offer_received", "Offer Received"), ("offer_accepted", "Offer Accepted"), ("sold", "Sold"), ("cancelled", "Cancelled") ],
        copy=False,
        default="new",
        required=True
    )

    salesman_id = fields.Many2one("res.users", string="Salesman", default=lambda self: self.env.user)
    buyer_id = fields.Many2one("res.partner", string="Buyer", copy=False)
    property_type_id = fields.Many2one("estate.property.type")
    property_tag_ids = fields.Many2many("estate.property.tag")
    offer_ids = fields.One2many("estate.property.offer", "property_id", string="Offers")

    total_area = fields.Integer(compute="_compute_total_area")

    best_price = fields.Float(compute="_compute_best_price")


    @api.depends("garden_area", "living_area")
    def _compute_total_area(self):
        for record in self:
            lr = record.living_area if record.living_area else 0
            gr = record.garden_area if record.garden_area else 0
            record.total_area = lr + gr

    @api.depends("offer_ids.price", "offer_ids.status")
    def _compute_best_price(self):
        for record in self:
            record.best_price = max(record.offer_ids.mapped(lambda x : 0 if x.status == 'refused' else x.price), default=0)

    @api.onchange("garden")
    def _onchange_garden(self):
        if self.garden:
            self.garden_area = 10
            self.garden_orientation = 'north'
        else:
            self.garden_area = 0
            self.garden_orientation = False
