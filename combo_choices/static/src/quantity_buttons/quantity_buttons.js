import { Component ,useState} from '@odoo/owl';

export class QuantityButtons extends Component {
    static template = 'combo_choices.QuantityButtons';

    static props = {
        quantity: Number,
        setQuantity: Function,
        btnClasses: { type: String, optional: true },
    };

    setup() {
        this.state = useState({quantity: this.props.quantity})
    }

    increaseQuantity() {
        this.props.setQuantity(this.state.quantity + 1);
        debugger;
    }

    decreaseQuantity() {
        if (this.state.quantity > 1) {  
            this.props.setQuantity(this.state.quantity - 1);  
        }
    }

    async setQuantity(event) {
        const quantity = parseFloat(event.target.value);
        this.state.quantity=quantity
    }
}
