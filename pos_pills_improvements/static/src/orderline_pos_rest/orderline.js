import { patch } from "@web/core/utils/patch";
import { onWillStart } from "@odoo/owl";
import { Orderline } from "@pos_preparation_display/app/components/orderline/orderline";

patch(Orderline.prototype, {
    setup() {
        super.setup();
        
        onWillStart(async () => {
            this.noteColor = await this.orm.call("pos.note", "get_color", [this.props.orderline.internalNote]);
        });
    },

    getColor(note) {
        return this.noteColor ? this.noteColor[note] : undefined;
    },
});
