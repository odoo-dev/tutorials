from odoo import api, fields, models


class FreightMD(models.Model):
    _name = "freight.md"
    _description = "Freight MD"

    name = fields.Char(string="Name", required=True)
    code = fields.Char(string="Code")
    country_id = fields.Many2one(
        "res.country",
        string="Country",
        required=True,
        options={"no_create": True, "no_open": True},
    )
    display_name = fields.Char(
        string="Display Name", compute="_compute_display_name", store=True
    )
    mode_select = fields.Many2many('mode.select', string='Is')

    status = fields.Boolean(string="Active", default=True)

    @api.depends("name", "country_id")
    def _compute_display_name(self):
        for record in self:
            if record.name and record.country_id:
                record.display_name = f"{record.name} - {record.country_id.name}"
            else:
                record.display_name = ""
    