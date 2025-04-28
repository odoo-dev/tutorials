/** @odoo-module **/

import { WebsiteSale } from '@website_sale/js/website_sale';

WebsiteSale.include({
    _getAdditionalDialogProps() {
        const props = this._super(...arguments);
        if (this.rootProduct.custom_image) {
            props.custom_image = this.rootProduct.custom_image;
        }
        return props;
    },

    _getAdditionalRpcParams() {
        const params = this._super(...arguments);
        if (this.rootProduct.custom_image) {
            params.custom_image = this.rootProduct.custom_image;
        }
        return params;
    },
});