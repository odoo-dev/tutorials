import { PosOrder } from "@point_of_sale/app/models/pos_order";
import { registry } from "@web/core/registry";

export class CustomerDisplayPosOrder extends PosOrder {
    getCustomerDisplayData() {
        const data = super.getCustomerDisplayData();

        return {
            ...data,
            lines: data.lines.map(line => ({
                ...line,
                isRefund: parseFloat(line.qty) < 0,
            })),
            totalRefundItems: data.lines.filter(line => parseFloat(line.qty) < 0).length,
            amountPerGuest: this.amountPerGuest().toFixed(2),
            customer_name: this.get_partner_name(),
        }
    }
}

registry.category("pos_available_models").add(PosOrder.pythonModel, CustomerDisplayPosOrder, { force: true });
