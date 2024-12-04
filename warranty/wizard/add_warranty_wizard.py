from odoo import api,fields,models,Command
class AddWarrantyWizard(models.TransientModel):
    _name="add.warranty.wizard"
    warranty_line_ids = fields.One2many('add.warranty.line', 'warranty_id')
    sale_order_id=fields.Many2one('sale.order', string="sale order id")

    @api.model
    def default_get(self, fields):
        res = super(AddWarrantyWizard, self).default_get(fields)
        context = {}
        sale_order_id = self.env.context.get("active_id")
        sale_order=self.env["sale.order"].browse(sale_order_id)

        warranty_line_vals=[]
        for line in sale_order.order_line:
            print("=*="*100)
            if line.product_template_id.warranty:
                warranty_line_vals.append(
                    Command.create(
                        {
                            "sale_order_line_id":line.id,
                            "product_id":line.product_template_id
                        }
                    )
                )
        res["warranty_line_ids"]=warranty_line_vals
        return res
        @api.model
        def add_warranty_action(self):
            # sale_order_id = self.env.context.get("active_id")
            # sale_order=self.env["sale.order"].browse(sale_order_id)
            # for record in self.warranty_line_ids:
            #     if record.warranty_config_id:
            pass
        