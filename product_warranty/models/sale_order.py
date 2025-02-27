from dateutil.relativedelta import relativedelta
from datetime import date
from odoo import api, fields, models


class SaleOrder(models.Model):
    _inherit = "sale.order"

    def action_open_warranty_wizard(self):
        view_id = self.env.ref('product_warranty.choose_warranty_view_form').id
        return {
            'name': 'Choose Warranty',
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'res_model': 'choose.warranty',
            'view_id': view_id,
            'views': [(view_id, 'form')],
            'target': 'new',
        }
