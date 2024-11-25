from odoo import models, fields, api

class EstatePropertyOffer(models.Model):
    _name = "estate.property.offer"
    _description = "Estate Property Offer Model"
    _order = "price desc"
    _sql_constraints = [
        ('price_positive', 'CHECK(price > 0)', "The offer price must be strictly positive.")
    ]
    price = fields.Float(required=True)
    partner_id = fields.Many2one("res.partner")
    status = fields.Selection(selection=[('accepted', 'Accepted'), ('refused', 'Refused')], copy=False)
    property_id = fields.Many2one("estate.property", required=True)
    property_type_id = fields.Many2one(related='property_id.property_type_id', store=True)
    # property_type_id = fields.Char(related='property_id.property_type_id', store=True)
    validity = fields.Integer(default=7)
    date_deadline = fields.Date(compute='_compute_date_deadline', inverse='_inverse_date_deadline')  

    @api.depends('create_date', 'validity')
    def _compute_date_deadline(self):
        for record in self:
            if record.create_date:
                record.date_deadline = fields.Date.add(record.create_date , days=record.validity)
            else:
                record.date_deadline = fields.Date.add(fields.Date.today(), days=record.validity)

    def _inverse_date_deadline(self):
        for record in self:
            if record.date_deadline and record.create_date:
                record.validity = (record.date_deadline - record.create_date.date()).days
            else:
                record.validity = 7
                record.date_deadline = fields.Date.add(fields.Date.today(), days=7)
                
    def action_accept_offer(self):
        for record in self:
            record.status = 'accepted'
            record.property_id.buyer = record.partner_id
            record.property_id.selling_price = record.price
        
        return True
    
    def action_reject_offer(self):
        for record in self:
            record.status = 'refused'
            # if record.property_id.buyer == record.partner_id:
            #     record.property_id.buyer = False
            #     record.property_id.selling_price = 0.0
            
            
        return True