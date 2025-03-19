import { patch } from "@web/core/utils/patch";
import { useService } from "@web/core/utils/hooks";
import { useState, useEffect } from "@odoo/owl";
import { Orderline } from "@point_of_sale/app/generic_components/orderline/orderline";

patch(Orderline.prototype, {
    setup() {
        this.orm = useService("orm");
        this.noteColor = useState({});

        useEffect(() => {
            const fetchColor = async () => {
                if (this.props.line.internalNote) {
                    let colorMap = await this.orm.call("pos.note", "get_color", [this.props.line.internalNote]);
                    Object.assign(this.noteColor, colorMap);
                }
            };
            fetchColor();
        }, () => [this.props.line.internalNote]);
    },

    getColor(note) {
        return this.noteColor[note];
    },
});
