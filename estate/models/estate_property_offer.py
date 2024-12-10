from odoo import api, fields, models
from datetime import datetime, timedelta
from odoo.exceptions import UserError 
class EstatePropertyOffer(models.Model):
    _name="estate.property.offer"
    _description="estate property offer model"
    _order="price desc"
    price=fields.Float()
    state = fields.Selection(
        [('accepted', 'Accepted'),
        ('refused' , 'Refused')
        ],copy=False,)
    partner_id=fields.Many2one('res.partner')
    property_id=fields.Many2one('estate.property', required=True)
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
    def _compute_validity(self):
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
            if record.state == "refused":
                raise UserError("Refused offer can be Accepted")
            else:   
                record.state="accepted"
                record.property_id.state="offer_accepted"
                record.property_id.selling_price=record.price
                record.property_id.partner_id=record.partner_id

    def action_do_refuse(self):
        for record in self:
            if record.state == "accepted":
                raise UserError("Accepted offer can be Refused")
            else:
                record.state="refused"

    #contraint for the price field.
    _sql_constraints=[('check_price','CHECK(price >=0 )',
    'The price msut be a Positive value')]
    property_type_id=fields.Many2one(related="property_id.property_type_id", store=True)

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            property = self.env['estate.property'].browse(vals.get("property_id"))
            
            # Update property state if it's "new"
            if property.state == "new":
                property.state = "offer_received"
            max_price = max(property.offer_ids.mapped('price'), default=0)
            if vals["price"] <= max_price:
                raise UserError(f"The offer must be higher than {max_price}.")
        
        # Call the super method to create the offers
        return super().create(vals_list)


    # def add_offer_action(self):
    #     property_ids = self.env.context.get("default_property_ids", [])
    #     for property_id in property_ids:
    #         offer = self.create({
    #             'price': self.price,
    #             'validity': self.validity,
    #             'partner_id': self.partner_id.id,
    #             'property_id': property_id,  # Use the property ID from the list
    #         })
    #     return {'type': 'ir.actions.act_window_close'}         
