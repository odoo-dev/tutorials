from odoo import _, api, models, fields

class ReturnPicking(models.TransientModel):
    _inherit = 'stock.return.picking'

    multi_records = fields.Boolean(default=False)
    show_so = fields.Boolean(default=False, compute='_compute_show_so')
    show_po = fields.Boolean(default=False, compute='_compute_show_po')

    @api.depends('picking_id')
    def _compute_show_so(self):
        pickings = self.env['stock.picking'].browse(self.env.context.get('active_records'))
        if len(pickings) > 1:
            self.multi_records = True
        self.show_so = self.picking_id.picking_type_id.code == 'outgoing' and self.multi_records

    @api.depends('picking_id')
    def _compute_show_po(self):
        pickings = self.env['stock.picking'].browse(self.env.context.get('active_records'))
        if len(pickings) > 1:
            self.multi_records = True
        self.show_po = self.picking_id.picking_type_id.code == 'incoming' and self.multi_records

    @api.model
    def default_get(self, fields):
        res = {}
        return_moves = []
        picking = self.env['stock.picking'].browse(self.env.context.get('active_id')) 
        pickings = self.env['stock.picking'].browse(self.env.context.get('active_records'))

        if len(pickings) > 1:
            for picking in pickings:
                for move in picking.move_ids:
                    return_moves.append((0,0, {
                        'product_id': move.product_id.id,
                        'move_id': move.id
                    }))
            res['product_return_moves'] = return_moves                
            res['multi_records'] = True
        else:
            res['multi_records'] = False
        if self.env.context.get('active_id') and self.env.context.get('active_model') == 'stock.picking':
            if picking.exists():
                res.update({'picking_id': picking.id})
        return res

    def _prepare_picking_default_values(self):
        location = self.picking_id.location_dest_id
        return_type = self.picking_id.picking_type_id.return_picking_type_id
        picking_name = self.picking_id.name
        new_origin = picking_name  
        
        if return_type and return_type.code == 'outgoing':
            location_dest = self.picking_id.location_id
            if self.multi_records:
                purchase_order_ids_str = ', '.join(
                    move_line.purchase_order_id.name 
                    for move_line in self.product_return_moves 
                    if move_line.purchase_order_id and move_line.purchase_order_id.name
                )
                new_origin = purchase_order_ids_str or new_origin
        else:
            location_dest = return_type.default_location_dest_id
            if self.multi_records:
                sale_order_ids_str = ', '.join(
                    move_line.sale_order_id.name 
                    for move_line in self.product_return_moves 
                    if move_line.sale_order_id and move_line.sale_order_id.name
                )
                new_origin = sale_order_ids_str or new_origin 

        vals = {
            'move_ids': [],
            'picking_type_id': self.picking_id.picking_type_id.return_picking_type_id.id or self.picking_id.picking_type_id.id,
            'state': 'draft',
            'return_id': self.picking_id.id,
            'origin': _("Return of %(picking_name)s", picking_name=new_origin), 
            'location_id': location.id,
            'location_dest_id': location_dest.id,
        }
        return vals

