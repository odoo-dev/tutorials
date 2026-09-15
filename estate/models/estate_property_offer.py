from odoo import api, models, fields
from odoo.exceptions import UserError
from odoo.tools import float_compare


class EstatePropertyOffer(models.Model):
    _name = 'estate.property.offer'
    _description = 'Estate Property Offer'
    _order = "price desc"

    price = fields.Float(
        string='Price',
    )
    status = fields.Selection(
        selection=[
            ('accepted', 'Accepted'),
            ('refused', 'Refused')
        ],
        copy=False,
        string='Status',
    )
    partner_id = fields.Many2one(
        comodel_name='res.partner',
        required=True,
        string='Partner',
    )
    property_id = fields.Many2one(
        comodel_name='estate.property',
        required=True,
        string='Property',
    )
    validity = fields.Integer(
        string='Validity',
        default=7,
    )
    date_deadline = fields.Date(
        string='Deadline',
        compute='_compute_date_deadline',
        inverse='_inverse_date_deadline',
    )

    property_type_id = fields.Many2one(
        related='property_id.property_type_id',
        store=True,
    )

    _check_price = models.Constraint(
        definition='CHECK(price > 0)',
        message='The offer price must be positive',
    )

    @api.depends("validity")
    def _compute_date_deadline(self):
        for record in self:
            create_date = record.create_date or fields.Date.today()
            record.date_deadline = fields.Date.add(
                create_date,
                days=record.validity,
            )

    def _inverse_date_deadline(self):
        for record in self:
            create_date = record.create_date or fields.Date.today()
            record.validity = (
                record.date_deadline - fields.Date.to_date(create_date)
            ).days

    @api.model
    def create(self, vals_list):
        if not isinstance(vals_list, list):
            vals_list = [vals_list]
        for vals in vals_list:
            if vals.get('property_id'):
                property_id = self.env['estate.property'].browse(vals['property_id'])
                if float_compare(vals.get('price', 0.0), property_id.best_price, precision_rounding=0.01) < 0:
                    raise UserError(self.env._("Cannot create offer with a lower price than the highest offer."))
                property_id.state = "offer_received"
        return super().create(vals_list)

    def action_accept(self):
        for record in self:
            if record.property_id.state in ('sold', 'canceled'):
                raise UserError(self.env._("Cannot accept offer for sold or canceled property."))

            record.status = 'accepted'

            accepted_offer = self.search([
                ('property_id', '=', record.property_id.id),
                ('id', '!=', record.id),
                ('status', '=', 'accepted'),
            ])

            accepted_offer.status = 'refused'

            record.property_id.state = 'offer_accepted'
            record.property_id.selling_price = record.price
            record.property_id.buyer = record.partner_id
        return True

    def action_refuse(self):
        for record in self:
            if record.property_id.state in ('sold', 'canceled'):
                raise UserError(self.env._("Cannot refuse offer for sold or canceled property."))

            if record.status == 'accepted':
                record.property_id.state = 'offer_received'
                record.property_id.buyer = False
                record.property_id.selling_price = False

            record.status = 'refused'
        return True
