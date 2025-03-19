import { patch } from "@web/core/utils/patch";
import { useState } from '@odoo/owl';
import { ComboConfiguratorPopup } from "@point_of_sale/app/store/combo_configurator_popup/combo_configurator_popup";
import { QuantityButtons } from "../quantity_buttons/quantity_buttons";

patch(ComboConfiguratorPopup, {
    components: {
        ...ComboConfiguratorPopup.components,
        QuantityButtons
    },
    props: {
        ...ComboConfiguratorPopup.props,
        showQuantity: { type: Boolean, optional: true }
    },

});


patch(ComboConfiguratorPopup.prototype, {
    setup() {
        super.setup();
        this.state = useState({
            ...this.state,
            quantity: 1 
        });
    },
    setQuantity(quantity) {
        console.log("quantity", quantity);
        console.log("quantityyy", this);
        if (quantity <= 0) quantity = 1;
        this.quantity = quantity;
        debugger;
    }
})          