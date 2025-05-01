/** @odoo-module **/

import { renderToElement } from "@web/core/utils/render";
import publicWidget from "@web/legacy/js/public/public_widget";

publicWidget.registry.saleOrder = publicWidget.Widget.extend({
    selector: '.s_sale_order_items',
    disabledInEditableMode: false,

    init: function () {
        this._super.apply(this, arguments);
        this.orm = this.bindService("orm");
        this.limit = 10;
        this.offset = 0;
        this.orders = [];
    },

    async willStart() {
        await this.loadMoreOrders();
    },

    async start() {
        this._super(...arguments);
        this.el.addEventListener('click', (ev) => {
            if (ev.target.matches('#load_more_btn')) {
                ev.preventDefault();
                this.loadMoreOrders();
            }
        });
    },

    async loadMoreOrders() {
        const showConfirmed = this.el.dataset.confirmOrders === 'true';
        const viewTemplate = this.el.dataset.layout || 'card';
        const domain = showConfirmed ? [['state', '=', 'sale']] : [];

        const new_orders = await this.orm.searchRead(
            'sale.order',
            domain,
            ['id', 'name', 'partner_id', 'state'],
            { offset: this.offset, limit: this.limit },
        );
        this.orders = this.orders.concat(new_orders);
        this.offset += this.limit;

        const tmpl = viewTemplate === 'list' ? 'website_sale_order.sale_order_list' : 'website_sale_order.sale_order_card';
        const $newContent = renderToElement(tmpl, { sale_orders: this.orders });
        this.$target[0].replaceChildren($newContent);
    },
});
