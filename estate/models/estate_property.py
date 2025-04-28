from odoo import api, fields, models
from odoo.exceptions import UserError
from dateutil.relativedelta import relativedelta


class EstatePropertyModel(models.Model):
    _name = "estate_property"
    _description = "Real estate properties"

    name = fields.Char("Title", required=True)
    property_type_id = fields.Many2one("estate_property_type", string="Property Type")
    description = fields.Text()
    postcode = fields.Char()
    date_availability = fields.Date(
        copy=False, default=fields.Date.today() + relativedelta(months=3)
    )
    expected_price = fields.Float(required=True)
    selling_price = fields.Float(readonly=True, copy=False, compute="_compute_selling_price")
    bedrooms = fields.Integer(default=2)
    living_area = fields.Integer()
    facades = fields.Integer()
    garage = fields.Boolean()
    garden = fields.Boolean()
    garden_area = fields.Integer()
    garden_orientation = fields.Selection(
        [
            ("north", "North"),
            ("south", "South"),
            ("east", "East"),
            ("west", "West"),
        ]
    )
    active = fields.Boolean(default=True)
    state = fields.Selection(
        [
            ("new", "New"),
            ("offer_received", "Offer Received"),
            ("offer_accepted", "Offer Accepted"),
            ("sold", "Sold"),
            ("cancelled", "Cancelled"),
        ],
        required=True,
        copy=False,
        default='new'
    )

    buyer_id = fields.Many2one("res.partner", copy=False, compute="_compute_buyer_id")
    salesperson_id = fields.Many2one("res.users", default=lambda self: self.env.user)
    tag_ids = fields.Many2many("estate_property_tag")
    offer_ids = fields.One2many("estate_property_offer", "property_id", string="Offers")

    total_area = fields.Integer(compute="_compute_area")
    best_price = fields.Float(compute="_compute_best_price")
    
    @api.depends("living_area", "garden_area")
    def _compute_area(self):
        for record in self:
            record.total_area = record.living_area + record.garden_area

    @api.depends("offer_ids")
    def _compute_best_price(self):
        for record in self:
            if record.offer_ids:
                record.best_price = min(record.offer_ids.mapped("price"))
            else:
                record.best_price = 0

    @api.depends("offer_ids")
    def _compute_selling_price(self):
        for record in self:
            record.selling_price = 0
            for offer in record.offer_ids:
                if hasattr(offer, "status") and getattr(offer, "status") == "accepted":
                    record.selling_price = offer.price
                    break

    @api.depends("offer_ids")
    def _compute_buyer_id(self):
        for record in self:
            record.buyer_id = None
            for offer in record.offer_ids:
                if hasattr(offer, "status") and getattr(offer, "status") == "accepted":
                    record.buyer_id = offer.partner_id
                    break

    @api.onchange("garden")
    def _onchange_garden(self):
        if self.garden:
            self.garden_area = 10
            self.garden_orientation = "north"
        else:
            self.garden_area = 0
            self.garden_orientation = None

    def action_set_property_sold(self):
        for record in self:
            if record.state == "cancelled":
                raise UserError("Cancelled properties cannot be sold")
            
            record.state = "sold"

        return True
    
    def action_set_property_cancelled(self):
        for record in self:
            if record.state == "sold":
                raise UserError("Sold properties cannot be cancelled")
            
            record.state = "cancelled"

        return True