from odoo import api, fields, models
from dateutil.relativedelta import relativedelta


class EstateProperty(models.Model):
    _name = "estate.property"
    _description = "Estate properties"

    active = fields.Boolean(string="Active", default=True)
    state = fields.Selection(
        string='State',
        selection=[('new', 'New'), ('received', 'Offer Received'), ('accepted', 'Offer Accepted'), ('sold', 'Sold'), ('cancelled', 'Cancelled')],
        required=True,
        copy=False,
        default='new'
    )
    name = fields.Char(string="Name", required=True, default='Unknown')
    description = fields.Text(string="Description")
    postcode = fields.Char(string="Postcode")
    date_availability = fields.Date(string="Availability", copy=False, default=fields.Date.today() + relativedelta(months=1))
    expected_price = fields.Float(string="Expected price", required=True)
    selling_price = fields.Float(string="Selling price", readonly=True, copy=False)
    bedrooms = fields.Integer(string="Bedrooms", default=2)
    living_area = fields.Integer(string="Living area")
    facades = fields.Integer(string="Facades")
    garage = fields.Boolean(string="Garage")
    garden = fields.Boolean(string="Garden")
    garden_area = fields.Integer(string="Garden area")
    garden_orientation = fields.Selection(
        string='Garden facing',
        selection=[('north', 'North'), ('south', 'South'), ('east', 'East'), ('west', 'West')],
        help="Garden facing")
    last_seen = fields.Date(string="Last seen", default=fields.Datetime.now)
    property_type_id = fields.Many2one("estate.property.type", string='Type')
    buyer = fields.Many2one('res.partner', string='Buyer')
    salesperson = fields.Many2one('res.users', string='Salesperson', index=True, tracking=True, default=lambda self: self.env.user)
    tags_ids = fields.Many2many("estate.property.tags", string='Tags')
    offer_ids = fields.One2many("estate.property.offer", "property_id", string="Offers")
    total_area = fields.Integer(compute=("_compute_total"))
    @api.depends("living_area", "garden_area")
    def _compute_total(self):
        for record in self:
            record.total_area = record.living_area + record.garden_area
    best_offer = fields.Float(compute="_compute_maximum")
    @api.depends("offer_ids.price")
    def _compute_maximum(self):
        for record in self:
            record.best_offer = max(p.price for p in record.offer_ids)
    validity = fields.Integer(compute="_compute_deadline", inverse="_compute_validity", string="Validity", default=7)
    date_deadline = fields.Date(compute="_compute_validity", inverse="_compute_deadline",string="Deadline", default=fields.Date.today())
    @api.depends("validity", "date_deadline")
    def _compute_deadline(self):
        for record in self:
            if record.create_date == 0:
                record.date_deadline = fields.Date.today() + relativedelta(days=record.validity)
            else:
                record.date_deadline = record.create_date + relativedelta(days=record.validity)
    def _compute_validity(self):
        for record in self:
            if record.create_date == 0:
                record.validity = 7
            else:
                record.validity = (record.date_deadline - record.create_date).day