import { Component } from "@odoo/owl";
import { usePos } from "@point_of_sale/app/hooks/pos_hook";

export class ClearOrderlineButton extends Component {
    static template = "point_of_sale.ClearOrderlineButton";
    static props = {
        icon: { type: String, optional: true },
        label: { type: String, optional: false },
        class: { type: String, optional: true }
    }

    setup(){
        this.pos = usePos();
    }

    onClick() {
        let selectedOrderline = this.pos.getOrder().getSelectedOrderline();
        if (selectedOrderline){
            this.pos.getOrder().removeOrderline(selectedOrderline);
        }
    }
}