from odoo import models,fields,api,Command

class WarrantyWizard(models.Model):
    _name = 'warranty.wizard'
    
    sale_order_id = fields.Many2one('sale.order', string="Sales Order")
    warranty_line_ids = fields.One2many('add.warranty.line.wizard', 'wizard_id', string="Warranty Lines") 
    
    @api.model
    def default_get(self, fields_list):
        default_values = super().default_get(fields_list)
        sales_order_id = self.env.context.get('active_id')
        
        if sales_order_id:
            sales_order = self.env['sale.order'].browse(sales_order_id)
            # sale_order_dict = sales_order.read()
            # print("Sales order object:", sale_order_dict)
            if not sales_order:
                return default_values
            
            warranty_lines = []
            for line in sales_order.order_line:
                if line.product_template_id.warranty:
                    warranty_lines.append(
                        Command.create(
                            {
                                "sale_order_line_id": line.id,
                                "product_id": line.product_template_id.id,
                            }
                        )
                    )
            default_values["sale_order_id"] = sales_order_id
            default_values["warranty_line_ids"] = warranty_lines
        return default_values
    
    def action_add_warranty(self):
        new_order_line_list = []
        for record in self:
            sale_order = record.sale_order_id  
            for line in record.warranty_line_ids:
                if line.warranty_config_id:  
                    new_order_line_list.append({
                        "order_id": sale_order.id,
                        "name": f"{line.warranty_config_id.name} / {line.end_date}",
                        "product_id": line.warranty_config_id.product_id.product_variant_id.id,  
                        "price_unit": line.sale_order_line_id.price_subtotal
                                    * (line.warranty_config_id.percentage / 100),  
                        "warranty_id": line.sale_order_line_id.id,  
                        "sequence": line.sale_order_line_id.sequence,  
                    })

        self.env["sale.order.line"].create(new_order_line_list)