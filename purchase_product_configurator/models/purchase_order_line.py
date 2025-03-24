from odoo import api, fields, models, _
from odoo.tools import groupby


class PurchaseProductVarient(models.Model):
    _inherit = 'purchase.order.line'

    configurable_product_template_id = fields.Many2one(
        comodel_name='product.template',
        string='Products Template',
        domain=[('purchase_ok', '=', True)],
        compute='_compute_product_template_id',
        search='_search_product_template_id'
    )
    configurable_product_template_attribute_value_ids = fields.Many2many(
        string="Product Attribute Values",
        related='product_id.product_template_attribute_value_ids',
        depends=['product_id']
    )
    configurable_product_custom_attribute_value_ids = fields.One2many(
        comodel_name='product.attribute.custom.value', inverse_name='purchase_order_line_id',
        string="Custom Values",
        compute='_compute_custom_attribute_values',
        store=True, precompute=True
    )
    configurable_product_no_variant_attribute_value_ids = fields.Many2many(
        comodel_name='product.template.attribute.value',
        relation='purchase_order_line_product_attr_rel_con',
        column1='order_line_id',
        column2='attribute_value_id',
        string="Extra Values",
        compute='_compute_no_variant_attribute_values',
        store=True,
        precompute=True,
        ondelete='restrict'
    )
    configurable_is_configurable_product = fields.Boolean('Is product configurable?',
        related="configurable_product_template_id.has_configurable_attributes"
    )

    @api.depends('product_id')
    def _compute_product_template_id(self):
        for line in self:
            line.configurable_product_template_id = line.product_id.product_tmpl_id

    def _search_product_template_id(self, operator, value):
        return [('product_id.product_tmpl_id', operator, value)]

    @api.depends('product_id')
    def _compute_custom_attribute_values(self):
        for line in self:
            if not line.product_id:
                line.configurable_product_custom_attribute_value_ids = False
                continue
            if not line.configurable_product_custom_attribute_value_ids:
                continue
            valid_values = line.product_id.product_tmpl_id.valid_product_template_attribute_line_ids.product_template_value_ids
            for pacv in line.configurable_product_custom_attribute_value_ids:
                if pacv.custom_product_template_attribute_value_id not in valid_values:
                    line.configurable_product_custom_attribute_value_ids -= pacv

    @api.depends('product_id')
    def _compute_no_variant_attribute_values(self):
        for line in self:
            if not line.product_id:
                line.configurable_product_no_variant_attribute_value_ids = False
                continue
            if not line.configurable_product_no_variant_attribute_value_ids:
                continue
            valid_values = line.product_id.product_tmpl_id.valid_product_template_attribute_line_ids.product_template_value_ids
            for ptav in line.configurable_product_no_variant_attribute_value_ids:
                if ptav._origin not in valid_values:
                    line.configurable_product_no_variant_attribute_value_ids -= ptav

    def _get_product_purchase_description(self, product):
        name = super(PurchaseProductVarient, self)._get_product_purchase_description(product)

        no_variant_ptavs = self.configurable_product_no_variant_attribute_value_ids._origin.filtered(
            lambda ptav: ptav.display_type == 'multi' or ptav.attribute_line_id.value_count > 1
        )
        if not self.configurable_product_custom_attribute_value_ids and not no_variant_ptavs:
            return name

        custom_ptavs = self.configurable_product_custom_attribute_value_ids.custom_product_template_attribute_value_id
        multi_ptavs = no_variant_ptavs.filtered(lambda ptav: ptav.display_type == 'multi').sorted()

        for ptav in (no_variant_ptavs - multi_ptavs - custom_ptavs):
            name += "\n" + ptav.display_name

        for pta, ptavs in groupby(multi_ptavs, lambda ptav: ptav.attribute_id):
            name += "\n" + _(pta.name +': '+ ", ".join(ptav.name for ptav in ptavs)
            )

        sorted_custom_ptav = self.configurable_product_custom_attribute_value_ids.custom_product_template_attribute_value_id.sorted()
        for patv in sorted_custom_ptav:
            pacv = self.configurable_product_custom_attribute_value_ids.filtered(lambda pcav: pcav.custom_product_template_attribute_value_id == patv)
            name += "\n" + pacv.display_name

        return name

    @api.onchange('product_id')
    def onchange_product_id(self):
        if not self.product_id or (self.env.context.get('origin_po_id') and self.product_qty):
            return
        self.price_unit = 0.0
        if self.product_qty < 1 or not self.product_id.product_template_attribute_value_ids:
            self.product_qty = 0.0
            self._suggest_quantity()
        self._product_id_change()

    @api.model
    def fields_get(self, allfields=None, attributes=None):
        res = super().fields_get(allfields, attributes)
        if 'product_template_id' in res:
            purchase_product_variant_mode = self.env['ir.config_parameter'].sudo().get_param('purchase.purchase_product_variant_mode')
            if purchase_product_variant_mode == 'matrix':
                res["configurable_product_template_id"]["column_invisible"] = "1"
            else:
                res["product_template_id"]["column_invisible"] = "1"
        return res


class ProductAttributeCustomValue(models.Model):
    _inherit = "product.attribute.custom.value"

    purchase_order_line_id = fields.Many2one('purchase.order.line', string="Purchase Order Line", ondelete='cascade')

    _sql_constraints = [
        ('pol_custom_value_unique', 'unique(custom_product_template_attribute_value_id, purchase_order_line_id)',
         "Only one Custom Value is allowed per Attribute Value per Purchase Order Line.")
    ]
