
import { Component, useState } from "@odoo/owl";
import { Counter } from "./counter";

export class Card extends Component {
    static template = "awesome_owl.card";
    static components = { Counter };
    
    setup() {
        this.countmul = useState({ value: 0 });
        this.hidden = useState({value: false})
        this.counts = useState({ value: {1: 0, 2: 0, 3: 0, 4: 0} });
        this.recalcMul = this.recalcMul.bind(this)
    }

    recalcMul(key, value) {
        this.counts.value[key] = value;
        this.countmul.value = 1;
        for (var i in this.counts.value) {
            this.countmul.value = this.countmul.value * this.counts.value[i]
        }
    }
    
    toggleHidden() {
        this.hidden.value = !this.hidden.value
    }
}
