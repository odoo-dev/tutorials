import { _t } from "@web/core/l10n/translation";
import { Component, markup } from "@odoo/owl";
import { patch } from "@web/core/utils/patch";
import { ReceiptHeader } from "@point_of_sale/app/screens/receipt_screen/receipt/receipt_header/receipt_header";
import { imageDataUri } from "@point_of_sale/utils";

patch(ReceiptHeader.prototype, {
    setup(){
       
        super.setup();
        console.log("bssdjkcbskdjbc",this.props)
       
    },

    get order() {
        return this.props.order;
    },

    get partnerAddress() {
        return this.order.partner_id?.pos_contact_address.split(/\n\n+/).join("\n").split("\n");
    },

    get vatText() {
        if (this.order.company.country_id?.vat_label) {
            return _t("%(vatLabel)s: %(vatId)s", {
                vatLabel: this.order.company.country_id.vat_label,
                vatId: this.order.company.vat,
            });
        }
        return _t("Tax ID: %(vatId)s", { vatId: this.order.company.vat });
    },

    get receiptLogoSrc() {
        if (this.order.config.receipt_logo) {
            return imageDataUri(this.order.config.receipt_logo);
        }
        return this.props.previewMode ? "/web/static/img/placeholder.png" : false;
    },

    get headerMarkup() {
        return markup(this.order.config.receipt_header);
    },


})

ReceiptHeader.props = {
    order: Object,
    previewMode: { type: Boolean, optional: true },
 
 };
 