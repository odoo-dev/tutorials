from datetime import datetime
from odoo.http import Controller, request, route


class PurchaseProductConfiguratorController(Controller):

    @route(route='/purchase/product_configurator/get_values', type='json', auth='user')
    def purchase_product_configurator_get_values(
        self,
        product_template_id,
        quantity,
        currency_id,
        so_date,
        product_uom_id=None,
        company_id=None,
        ptav_ids=None,
        **kwargs,
    ):
        if company_id:
            request.update_context(allowed_company_ids=[company_id])
        product_template = request.env['product.template'].browse(product_template_id)
        combination = request.env['product.template.attribute.value']
        if ptav_ids:
            combination = request.env['product.template.attribute.value'].browse(ptav_ids).filtered(
                lambda ptav: ptav.product_tmpl_id.id == product_template_id
            )
            unconfigured_ptals = (
                product_template.attribute_line_ids - combination.attribute_line_id).filtered(
                lambda ptal: ptal.attribute_id.display_type != 'multi')
            combination += unconfigured_ptals.mapped(
                lambda ptal: ptal.product_template_value_ids._only_active()[:1]
            )
        if not combination:
            combination = product_template._get_first_possible_combination()
        currency = request.env['res.currency'].browse(currency_id)
        so_date = datetime.fromisoformat(so_date)
        partnerId = kwargs.get('partnerId') or None
        if not quantity:
            seller_min_qty = product_template.seller_ids\
                .filtered(lambda r: r.partner_id.id == partnerId and (not r.product_id or r.product_id.product_tmpl_id == product_template.id))\
                .sorted(key=lambda r: r.min_qty)
            if seller_min_qty:
                quantity = int(seller_min_qty[0].min_qty)
                product_uom_id = seller_min_qty[0].product_uom
            else:
                quantity = 1

        return dict(
            products=[
                dict(
                    **self._get_product_information(
                        product_template,
                        combination,
                        currency,
                        so_date,
                        quantity=quantity,
                        product_uom_id=product_uom_id,
                        company_id=company_id,
                        **kwargs,
                    ),
                )
            ],
            optional_products=[],
            currency_id=currency_id,
        )

    @route(
        route='/purchase/product_configurator/create_product',
        type='json',
        auth='user',
        methods=['POST'],
    )
    def purchase_product_configurator_create_product(self, product_template_id, ptav_ids):
        product_template = request.env['product.template'].browse(product_template_id)
        combination = request.env['product.template.attribute.value'].browse(ptav_ids)
        product = product_template._create_product_variant(combination)
        return product.id

    @route(
        route='/purchase/product_configurator/update_combination',
        type='json',
        auth='user',
        methods=['POST'],
    )
    def purchase_product_configurator_update_combination(
        self,
        product_template_id,
        ptav_ids,
        currency_id,
        so_date,
        quantity,
        product_uom_id=None,
        company_id=None,
        **kwargs,
    ):
        if company_id:
            request.update_context(allowed_company_ids=[company_id])
        product_template = request.env['product.template'].browse(product_template_id)
        product_uom = request.env['uom.uom'].browse(product_uom_id)
        currency = request.env['res.currency'].browse(currency_id)
        combination = request.env['product.template.attribute.value'].browse(ptav_ids)
        product = product_template._get_variant_for_combination(combination)

        return self._get_basic_product_information(
            product or product_template,
            combination,
            quantity=quantity or 0.0,
            uom=product_uom,
            currency=currency,
            date=datetime.fromisoformat(so_date),
            company_id=company_id,
            **kwargs,
        )

    def _get_product_information(
        self,
        product_template,
        combination,
        currency,
        so_date,
        quantity=1,
        product_uom_id=None,
        parent_combination=None,
        **kwargs,
    ):
        if not product_uom_id or isinstance(product_uom_id, int):
            product_uom = request.env['uom.uom'].browse(product_uom_id)
        else:
            product_uom = product_uom_id
        product = product_template._get_variant_for_combination(combination)
        attribute_exclusions = product_template._get_attribute_exclusions(
            parent_combination=parent_combination,
            combination_ids=combination.ids,
        )
        product_or_template = product or product_template
        return dict(
            product_tmpl_id=product_template.id,
            **self._get_basic_product_information(
                product_or_template,
                combination,
                quantity=quantity,
                uom=product_uom,
                currency=currency,
                date=so_date,
                **kwargs,
            ),
            quantity=quantity,
            attribute_lines=[dict(
                id=ptal.id,
                attribute=dict(**ptal.attribute_id.read(['id', 'name', 'display_type'])[0]),
                attribute_values=[
                    dict(
                        **ptav.read(['name', 'html_color', 'image', 'is_custom'])[0],
                        price_extra=0.0,
                    ) for ptav in ptal.product_template_value_ids
                    if ptav.ptav_active or combination and ptav.id in combination.ids
                ],
                selected_attribute_value_ids=combination.filtered(
                    lambda c: ptal in c.attribute_line_id
                ).ids,
                create_variant=ptal.attribute_id.create_variant,
            ) for ptal in product_template.attribute_line_ids],
            exclusions=attribute_exclusions['exclusions'],
            archived_combinations=attribute_exclusions['archived_combinations'],
            parent_exclusions=attribute_exclusions['parent_exclusions'],
        )

    def _get_basic_product_information(self, product_or_template, combination, **kwargs):
        basic_information = dict(
            **product_or_template.read(['description_sale', 'display_name'])[0]
        )
        price = 0.0
        if not product_or_template.is_product_variant:
            basic_information['id'] = False
            combination_name = combination._get_combination_name()
            if combination_name:
                basic_information.update(
                    display_name=f"{basic_information['display_name']} ({combination_name})"
                )
        else:
            partnerId = kwargs.get('partnerId') or None
            partner_id = request.env['res.partner'].search([('id','=',partnerId)])
            date=kwargs.get('date')
            uom_id=kwargs.get('uom')
            quantity=kwargs.get('quantity')
            currency_id=kwargs.get('currency')
            company_id=kwargs.get('company_id')
            seller = product_or_template._select_seller(
                partner_id=partner_id,
                quantity=quantity,
                date=date,
                uom_id=uom_id,
            )
            if seller:
                price = seller.currency_id._convert(seller.price, currency_id, company_id, date, True)
                price = seller.product_uom._compute_price(price, uom_id)
            else:
                price = product_or_template.currency_id._convert(product_or_template.standard_price, currency_id, company_id, date, True)

        return dict(
            **basic_information,
            price= price,
        )
