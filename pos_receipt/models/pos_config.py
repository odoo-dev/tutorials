from odoo import fields, models


class PosConfig(models.Model):
    _inherit = 'pos.config'

    receipt_layout = fields.Selection([('light', 'Light'), ('boxes', 'Boxes'), ('lined', 'Lined')], string='Receipt Layout', default='light')
    receipt_header = fields.Html(string='Receipt Header', translate=True, help="Company details, which is included in a printed receipt's header.")
    receipt_footer = fields.Html(string='Receipt Footer', translate=True, help='A short info or tagline that will be inserted as a footer in the printed receipt.')
    receipt_logo = fields.Binary(string='Receipt Logo', default=lambda self: self.env.company.logo, help='A logo that will be printed in the receipt.')
    receipt_bg_layout = fields.Selection([('blank', 'Blank'), ('demo_logo', 'Demo logo'), ('custom', 'Custom')], default='blank', string='Background Layout', required=True)
    receipt_bg_image = fields.Binary(string='Receipt Background Image', help='A logo that will be printed in the receipt.')
    receipt_font = fields.Selection([('Lato', 'Lato'), ('Roboto', 'Roboto'), ('Open_Sans', 'Open Sans'), ('Montserrat', 'Montserrat'), ('Oswald', 'Oswald'), ('Raleway', 'Raleway'), ('Tajawal', 'Tajawal'), ('Fira_Mono', 'Fira Mono')], default='Lato')
