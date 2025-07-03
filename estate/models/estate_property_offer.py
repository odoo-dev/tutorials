from dateutil.relativedelta import relativedelta

from odoo import api, fields, models

class EstatePropertyOffer(models.Model):
    _name = "estate.property.offer"
    _description = """
    Offers containing price, status, partner_id and property_id
    """
    _sql_constraints = [
        ('check_offer_price', 'CHECK(price >= 0)', 'The offer price must be strictly positive.')
    ]
    _order = "price desc"

    price = fields.Float(default=0)
    status = fields.Selection(
        selection=[
            ('accepted', 'Accepted'),
            ('refused', 'Refused'),
        ],
        copy=False,
    )
    property_type_id = fields.Many2one('estate.property.type', related='property_id.property_type_id', String="Offers", store=True)
    partner_id = fields.Many2one('res.partner', required=True)
    property_id = fields.Many2one('estate.property', required=True)

    create_date = fields.Date(default = fields.Date.today())
    validity = fields.Integer(default=7)
    date_deadline=fields.Date(compute="_compute_deadline", inverse="_inverse_deadline")

    @api.depends("validity", "date_deadline")
    def _compute_deadline(self):
        for record in self:
            record.date_deadline = record.create_date + relativedelta(days = record.validity)
    
    def _inverse_deadline(self):
        for record in self:
            record.validity = (record.date_deadline - fields.Date.today()).days

    def accept_offer(self):
        self.status = 'accepted'
        self.property_id.state = 'offer_accepted'
        self.property_id.selling_price = self.price
        self.property_id.buyer_id = self.partner_id.id
        return True
    
    def refuse_offer(self):
        self.status = 'refused'
        return True