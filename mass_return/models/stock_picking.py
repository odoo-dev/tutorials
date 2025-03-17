from odoo import fields, models

class StockPicking(models.Model):
    _inherit = 'stock.picking'   

    def _compute_is_origin_visible(self):
        if len(self.ids) > 1:
            self.is_origin_visible = True

    def action_mass_return(self):
        return {
            'name': 'Mass Return (Deliveries)',
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'res_model': 'stock.return.picking',
            'target': 'new',
            'view_id': self.env.ref('stock.view_stock_return_picking_form').id,
            'context': {
                'active_records': self.ids,
            }
        }
