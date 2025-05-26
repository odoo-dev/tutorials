import { Component, useEffect } from "@odoo/owl";
import { humanNumber } from "@web/core/utils/numbers";

export class ClickValue extends Component { 
    static template = "clicker_game.click_value";
    static props = {
        value: { type: Object, optional: true },
    };
    static defaultProps = { 
        value: { count: 0.0 },
    };

    setup() {   
        super.setup();
        this.value = humanNumber(this.props.value.count, { decimals: 1 });
        useEffect(() => {
            this.value = humanNumber(this.props.value.count, { decimals: 1 });
        }, () => [this.props.value.count]);
    }
}
