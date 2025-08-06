from dateutil.relativedelta import relativedelta
from odoo import api, fields, models


class EstatePropertyOffer(models.Model):
    _name = 'estate.property.offer'
    _description = 'Estate Property Offer'

    price = fields.Float(string='Price', required=True)
    status = fields.Selection(selection=[('accepted', 'Accepted'), ('refused', 'Refused')], string='Status', copy=False)
    partner_id = fields.Many2one('res.partner', string='Partner', required=True)
    property_id = fields.Many2one('estate.property', string='Property', required=True, ondelete='cascade')
    validity = fields.Integer(string='Validity (days)', default=7)
    create_date = fields.Date(string='Creation Date', default=fields.Datetime.today(), readonly=True)
    date_deadline = fields.Date(string='Deadline', compute='_compute_date_deadline', inverse='_compute_validity',
                                store=True)

    @api.depends('validity')
    def _compute_date_deadline(self):
        for record in self:
            record.date_deadline = record.create_date + relativedelta(
                days=record.validity)

    def _compute_validity(self):
        for record in self:
            if record.date_deadline:
                delta = record.date_deadline - fields.Date.today()
                record.validity = delta.days if delta.days > 0 else 0
