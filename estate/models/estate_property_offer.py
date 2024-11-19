from odoo import api, fields, models
from datetime import datetime, timedelta
from odoo.exceptions import UserError 
class EstatePeopertyOffer(models.Model):
    _name="estate.property.offer"
    _description="estate property offer model"
    _order="price desc"
    price=fields.Float()
    status = fields.Selection(
        [('accepted', 'Accepted'),
        ('refused' , 'Refused')
        ],copy=False,)
    partner_id=fields.Many2one('res.partner')
    property_id=fields.Many2one('estate.property')
    validity=fields.Integer(compute="_compute_validity",inverse="_inverse_validity", default=7, store=True)
    date_deadline=fields.Date(compute="_compute_date_deadline", inverse="_inverse_date_deadline", store=True)
   

    @api.depends("validity")
    def _compute_date_deadline(self):
         for record in self:
            if record.validity and record.create_date:
                record.date_deadline = (record.create_date + timedelta(days=record.validity)).date()
    def _inverse_date_deadline(self):
        for record in self:
            if record.date_deadline and record.create_date:
                delta = record.date_deadline - record.create_date.date()
                record.validity = delta.days

    @api.depends("date_deadline")
    def _compute_validity():
        for record in self:
            if record.create_date and record.date_deadline:
                delta = record.date_deadline - record.create_date.date()
                record.validity = delta.days

    def _inverse_validity(self):            
        for record in self:
                if record.validity and record.create_date:
                    record.date_deadline = (record.create_date + timedelta(days=record.validity)).date()
    def action_do_accept(self):
        for record in self:
            if record.status == "refused":
                raise UserError("Refused offer can be Accepted")
            else:   
                record.status="accepted"
                record.property_id.selling_price=record.price
                record.property_id.partner_id=record.partner_id

    def action_do_refuse(self):
        for record in self:
            if record.status == "accepted":
                raise UserError("Accepted offer can be Refused")
            else:
                record.status="refused"

    #contraint for the price field.
    _sql_constraints=[('check_price','CHECK(price >=0 )',
    'The price msut be a Positive value')]      



     








