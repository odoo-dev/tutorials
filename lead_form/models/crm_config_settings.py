import random
import string
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    lead_form_enabled = fields.Boolean(
        string='Enable Lead Form',
        config_parameter='lead_form.lead_form_enabled',
        help="Enable or disable the lead form feature.",
        default=True
    )

    webhook_url = fields.Char(
        string='Lead Form URL',
        config_parameter='lead_form.lead_form_url',
        help="URL for the lead form.",
    )

    verify_token = fields.Char(
        config_parameter='lead_form.verify_token',
        help="Token for verifying the webhook.",
    )


    @api.model
    def get_values(self):
        res = super().get_values()
        IrConfig = self.env['ir.config_parameter'].sudo()
        res.update(
            lead_form_enabled=IrConfig.get_param('lead_form.lead_form_enabled') == 'True',
            webhook_url=IrConfig.get_param('lead_form.lead_form_url'),
            verify_token=IrConfig.get_param('lead_form.verify_token'),
        )
        return res

    def set_values(self):
        IrConfig = self.env['ir.config_parameter'].sudo()
        previous_enabled = IrConfig.get_param('lead_form.lead_form_enabled') == 'True'

        super().set_values()

        if not previous_enabled and self.lead_form_enabled:
            # Lead form just got enabled
            existing_url = IrConfig.get_param('lead_form.lead_form_url')
            existing_token = IrConfig.get_param('lead_form.verify_token')

            if existing_url or existing_token:
                token = ''.join(random.choices(string.ascii_letters + string.digits, k=6))
                IrConfig.set_param('lead_form.verify_token', token)
                return  # Skip creation if URL or token already exists

            # Generate a random token
            token = ''.join(random.choices(string.ascii_letters + string.digits, k=6))

            # Find model_id for crm.lead (Lead/Opportunity)
            model = self.env['ir.model'].sudo().search([('model', '=', 'crm.lead')], limit=1)
            if not model:
                raise ValidationError("Model crm.lead not found.")

            # Create base.automation record
            rule = self.env['base.automation'].sudo().create({
                'name': 'Ads Lead Form',
                'trigger': 'on_webhook',
                'model_id': model.id,
            })

            # Save webhook_url and verify_token
            IrConfig.set_param('lead_form.lead_form_url', rule.url)
            IrConfig.set_param('lead_form.verify_token', token)
        else:
            IrConfig.set_param('lead_form.verify_token', "")

