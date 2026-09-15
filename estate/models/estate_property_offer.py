from odoo import api, models, fields, _
from odoo.exceptions import UserError


class EstatePropertyOffer(models.Model):
    # Private attributes
    _name = "estate.property.offer"
    _description = "Estate property offer"
    _order = "price desc"

    # Field declarations
    price = fields.Float()
    status = fields.Selection(
        copy=False,
        selection=[("accepted", "Accepted"), ("refused", "Refused")],
    )
    validity = fields.Integer(default=7)
    date_deadline = fields.Date(
        compute="_compute_deadline", inverse="_inverse_deadline"
    )

    partner_id = fields.Many2one("res.partner", required=True)
    property_id = fields.Many2one("estate.property", required=True)
    property_type_id = fields.Many2one(
        "estate.property.type", string="Type", related="property_id.property_type_id"
    )

    # SQL constraints and indexes
    _price_constraint = models.Constraint(
        "CHECK (price > 0)", "Price must be positive."
    )

    # Compute, inverse and search methods
    @api.depends("validity", "create_date")
    def _compute_deadline(self):
        for record in self:
            base_date = (
                record.create_date.date() if record.create_date else fields.Date.today()
            )
            record.date_deadline = fields.Date.add(base_date, days=record.validity)

    def _inverse_deadline(self):
        for record in self:
            if not record.date_deadline:
                continue
            base_date = (
                record.create_date.date() if record.create_date else fields.Date.today()
            )
            record.validity = (record.date_deadline - base_date).days

    # CRUD methods
    @api.model
    def create(self, vals):
        for record in vals:
            self.env['estate.property'].browse(record['property_id']).action_change_state("offer_recieved")
        return super().create(vals)

    # Action methods
    def action_confirm(self):
        for record in self:
            if record.property_id.state in ["sold", "cancelled"]:
                raise UserError(_("Property already sold, or cancelled"))
            record.property_id.action_sell_to_offer(
                offer_buyer_id=record.partner_id, offer_selling_price=record.price
            )
            record.status = "accepted"

    def action_refuse(self):
        self.status = "refused"
