from odoo import api,fields, models
from dateutil.relativedelta import relativedelta

class estateProperty(models.Model):
    _name = "estate.property"
    _description = "Estate Property Model"
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(required=True, string='Name', tracking=True)
    description = fields.Text(tracking=True)
    postcode= fields.Char()
    tag_ids = fields.Many2many("estate.property.tag", string="Tags")
    property_type_id = fields.Many2one('estate.property.type', string="Property Type")
    date_availability=fields.Date(copy=False, default=fields.Date.today()+relativedelta(months=3), string='Available From', tracking=True)
    expected_price=fields.Float(required=True,tracking=True)
    selling_price=fields.Float(readonly=True, copy=False,tracking=True)
    bedrooms=fields.Integer(default=2, tracking=True)
    living_area=fields.Integer(string='Living Area (sqm)', tracking=True)
    facades=fields.Integer(tracking=True)
    active = fields.Boolean(default=True, tracking=True)
    garage=fields.Boolean(tracking=True)
    buyer_id = fields.Many2one('res.partner',string="Buyer",copy=False, tracking=True)
    salesperson_id = fields.Many2one('res.users', string="Salesperson", tracking=True, default=lambda self: self.env.user )
    offer_ids = fields.One2many("estate.property.offer", "property_id", string=" ")
    state = fields.Selection(
        string='State',
        selection=[('new', 'New'), ('offer_recieved', 'Offer Recieved'), ('offer_accepted', 'Offer Accepted'), ('sold', 'Sold'), ('canceled', 'Canceled')],
        required=True,
        copy=False,
        default='new',
        tracking=True
    )
    garden=fields.Boolean(tracking=True)
    garden_area=fields.Integer()
    garden_orientation=fields.Selection(
        string='Garden Orientation',
        selection=[('north', 'North'), ('south', 'South'), ('east', 'East'), ('west', 'West')],
        tracking=True
    )
    total_area = fields.Integer(compute="_compute_total_area", string='Total Area (sqm)')
    best_price = fields.Float(compute="_compute_best_price", string ="Best Price")

    @api.depends('garden_area','living_area')
    def _compute_total_area(self):
        for record in self:
            record.total_area = record.garden_area + record.living_area

    @api.depends("offer_ids.price")
    def _compute_best_price(self):
        for record in self:
            prices = [offer.price for offer in record.offer_ids]
            if prices:
                record.best_price = max(prices)
            else:
                record.best_price = 0
                
    @api.onchange("garden")
    def _onchange_garden(self):
        if(self.garden):
            self.garden_area = 20
            self.garden_orientation = 'north'
        else:
            self.garden_area = None
            self.garden_orientation = None
