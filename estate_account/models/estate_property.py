from odoo import fields, models

class InheritedPropertyEstate(models.Model):
    _inherit="estate.property"
    #override method action_do_sold 
    def action_do_sold(self):
        print("overriden method called of child class")
        return super().action_do_sold()   
