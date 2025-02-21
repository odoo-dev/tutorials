# -*- coding: utf-8 -*-

from odoo.addons.payment.controllers import portal as payment_portal
from odoo.http import request


class PaymentPortal(payment_portal.PaymentPortal):

    def _create_transaction(self, *args, **kwargs):
        tx_sudo = super()._create_transaction(*args, **kwargs)
        sale_order = request.env['sale.order'].sudo().browse(kwargs.get('sale_order_id'))
        
        if sale_order.exists():
            tx_sudo.partner_id = sale_order.partner_id.id

        return tx_sudo