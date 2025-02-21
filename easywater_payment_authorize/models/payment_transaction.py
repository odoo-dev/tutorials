# -*- coding: utf-8 -*-

from odoo import models


class PaymentTransaction(models.Model):
    _inherit = 'payment.transaction'

    def _authorize_create_transaction_request(self, opaque_data):
        self.ensure_one()
        if self.partner_id:
            self.update({
                'partner_name': self.partner_id.name,
                'partner_email': self.partner_id.email,
                'partner_phone': self.partner_id.phone,
                'partner_address': self.partner_id.street,
                'partner_city': self.partner_id.city,
                'partner_zip': self.partner_id.zip,
                'partner_state_id': self.partner_id.state_id.id or False,
                'partner_country_id': self.partner_id.country_id.id or False,
            })

        return super()._authorize_create_transaction_request(opaque_data)