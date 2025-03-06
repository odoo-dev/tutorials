import { patch } from "@web/core/utils/patch";
import { OrderReceipt } from "@point_of_sale/app/screens/receipt_screen/receipt/order_receipt";

patch(OrderReceipt, {

    props: {
        ...OrderReceipt.props,
        simplified_receipt: { type: Boolean, optional: true },
    },
    defaultProps: {
        ...OrderReceipt.defaultProps,
        simplified_receipt: false,
    },
})

patch(OrderReceipt.prototype, {
    setup() {
        super.setup();
        this.generateMenuLines()
    },
    generateMenuLines() {
        let count = this.props.data.headerData.customer_count;
        let price = parseFloat(this.props.data.total_paid) || 0;  
        let pricePerGuest = (price / count).toFixed(2);
        let lines = [];
        for (let i = 0; i < count; i++) {
            lines.push({ id: i, name: `Menu Item ${i + 1}  ` ,price:  pricePerGuest});
        }
        this.customer = lines;
    },
})
