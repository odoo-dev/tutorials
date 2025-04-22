from odoo import fields, models


class SignItemType(models.Model):
    _inherit = 'sign.item.type'

    # Added a new selection option "Stamp" to the existing item_type field with cascade deletion behavior
    item_type = fields.Selection(
        selection_add=[("stamp", "Stamp")],
        ondelete={"stamp": "cascade"}
    )
