from odoo import models
from odoo.exceptions import ValidationError

class EstatePropertyOffer(models.Model):
    _inherit = "estate.property.offer"

    def action_accept(self, from_cron=False):
        """Accept an offer and notify the partner."""
        for offer in self:
            if offer.property_id.state == "auction" and not from_cron:
                raise ValidationError("You cannot accept an offer when the property state is 'Auction'.")

            res = super().action_accept()  # Call the original method

            # Send email to the accepted partner
            self._send_offer_email(offer.partner_id, offer.price, accepted=True)

            # Send email to all rejected partners
            rejected_offers = self.search([
                ('property_id', '=', offer.property_id.id),
                ('id', '!=', offer.id),  # Exclude the accepted offer
                ('status', 'not in', ['offer_accepted', 'refused'])  # Exclude already rejected offers
            ])
            for rejected_offer in rejected_offers:
                self._send_offer_email(rejected_offer.partner_id, rejected_offer.price, accepted=False)

        return res

    def action_reject(self):
        for offer in self:
            if offer.property_id.state == "auction":  # Ensure property_id is a Many2one to estate.property
                raise ValidationError("You cannot reject an offer when the property state is 'Auction'.")
        return super().action_reject()

    def _send_offer_email(self, partner, price, accepted):
        """Send an email to the partner about their offer status."""
        mail_template = self.env.ref('automated_real_estate_auction.offer_accepted_email_template' if accepted
                                     else 'automated_real_estate_auction.offer_rejected_email_template')
        if mail_template:
            mail_template.sudo().send_mail(self.id, force_send=True)
