from odoo import api, fields, models


class Property(models.Model):
    _name = "estate.property"
    _description = "Real Estate property"
    
    name = fields.Char("Title", required=True)
    description = fields.Text("Description")
    postcode = fields.Char("Postcode")
    date_availability = fields.Date("Available Date", copy=False, default=fields.Date.add(fields.Date.today(), months=3))
    expected_price = fields.Float("Expected price", required=True)
    selling_price = fields.Float("Selling price", readonly=True, copy=False)
    bedrooms = fields.Integer("Bedrooms", default=2)
    living_area = fields.Integer("Living area (sqm)")
    facades = fields.Integer("Facades")
    garage = fields.Boolean("Garage")
    garden = fields.Boolean("Garden")
    garden_area = fields.Integer("Garden area (sqm)")
    garden_orientation = fields.Selection([("north", "North"), ("south", "South"), ("east", "East"), ("west", "West")], string = "Garden Orientation")
    active = fields.Boolean("Active", default=True)
    state = fields.Selection([("new", "New"), ("offer_received", "Offer Received"), ("offer_accepted", "Offer Accepted"), ("sold", "Sold"), ("canceled", "Canceled")], string="State", required=True, copy=False, default="new")
    
    property_type_id = fields.Many2one("estate.property.type", string="Property Type")
    salesman_id = fields.Many2one("res.users", string="Salesman", default=lambda self: self.env.user)
    buyer_id = fields.Many2one("res.users", string="Buyer", copy=False)
    tag_ids = fields.Many2many("estate.property.tag", string = "Tags")
    offer_ids = fields.One2many("estate.property.offer", "property_id", string="Offers")
    
    total_area = fields.Float("Total area (sqm)", compute="_compute_area")
    best_price = fields.Float("Best price", compute="_compute_best_price")
    
    @api.depends("living_area", "garden_area")
    def _compute_area(self):
        for record in self:
            record.total_area = record.living_area + record.garden_area

    @api.depends("offer_ids.price")
    def _compute_best_price(self):
        for record in self:
            record.best_price = max([0]+record.offer_ids.mapped('price'))
    
    @api.onchange("garden")
    def _onchange_garden(self):
        if self.garden:
            self.garden_area = 10
            self.garden_orientation = "north"
        else:
            self.garden_area = 0
            self.garden_orientation = ""