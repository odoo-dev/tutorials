import { patch } from "@web/core/utils/patch";
import { ReceiptScreen } from "@point_of_sale/app/screens/receipt_screen/receipt_screen";
import { useTrackedAsync } from "@point_of_sale/app/utils/hooks";
patch(ReceiptScreen.prototype, {
    setup() {
        super.setup();
        this.doSimpleReceipt = useTrackedAsync(() => this.pos.printReceipt({simple: true}))
    },
})
