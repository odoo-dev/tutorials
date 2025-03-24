import { ProductConfiguratorDialog } from "@sale/js/product_configurator_dialog/product_configurator_dialog";
import { ProductLabelSectionAndNoteListRender } from "@account/components/product_label_section_and_note_field/product_label_section_and_note_field";
import { patch } from "@web/core/utils/patch";

export class PurchaseProductConfiguratorDialog extends ProductConfiguratorDialog {

    static props = {
        ...ProductConfiguratorDialog.props,
        partnerId: { type: Number, optional: true },
    };

    setup() {
        super.setup();
        this.getValuesUrl = '/purchase/product_configurator/get_values';
        this.updateCombinationUrl = '/purchase/product_configurator/update_combination';
        this.createProductUrl = '/purchase/product_configurator/create_product';
    }

    _getAdditionalRpcParams() {
        const params = super._getAdditionalRpcParams();
        params.partnerId = this.props.partnerId;
        return params;
    }
}

patch(ProductLabelSectionAndNoteListRender.prototype, {
    setup() {
        super.setup();
        this.productColumns.push("configurable_product_template_id");
    }
});
