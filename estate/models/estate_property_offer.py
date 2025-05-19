from odoo import api, fields, models
from odoo.exceptions import UserError, ValidationError


class EstatePropertyOffer(models.Model):
    _name = 'estate.property.offer'
    _description = 'Property Offer'
    _order = 'price desc'
    _sql_constraints = [
        ('positive_price', 'check (price > 0)', 'The offer price must be positive.'),
    ]

    price = fields.Float()
    status = fields.Selection(selection=[('accepted', 'Accepted'), ('refused', 'Refused')], copy=False)
    validity = fields.Integer(default=7, string="Validity (days)")
    date_deadline = fields.Date(compute='_compute_deadline', inverse='_inverse_deadline', string="Deadline")

    partner_id = fields.Many2one(
        comodel_name='res.partner',
        string="Partner",
        required=True)
    property_id = fields.Many2one(
        comodel_name='estate.property',
        string="Property",
        required=True)
    property_type_id = fields.Many2one(
        related='property_id.property_type_id',
        string="Property Type",
        store=True)

    @api.depends('validity')
    def _compute_deadline(self):
        for record in self:
            if record.create_date:
                record.date_deadline = fields.Date.add(record.create_date, days=record.validity)
            else:
                record.date_deadline = fields.Date.add(fields.Date.today(), days=record.validity)

    def _inverse_deadline(self):
        for record in self:
            base_date = record.create_date.date() if record.create_date else fields.Date.today()
            record.validity = abs(record.date_deadline - base_date).days

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            property_record = self.env['estate.property'].browse(vals['property_id'])
            if property_record.offer_ids and min(property_record.offer_ids.mapped('price')) > vals['price']:
                raise UserError("Can't add offer with price lower than existing offer")
            if property_record.state == 'sold':
                raise ValidationError("Can't create offer for sold property")
            property_record.state = 'offer_received'
        return super().create(vals_list)

    def action_accept(self):
        for record in self:
            record.status = 'accepted'
            record.property_id.buyer_id = record.partner_id
            record.property_id.selling_price = record.price
            record.property_id.state = 'offer_accepted'
            for offer in record.property_id.offer_ids:
                if offer.id != record.id:
                    offer.action_refuse()
        return True

    def action_refuse(self):
        for record in self:
            record.status = 'refused'
        return True
