import { Navbar } from "@point_of_sale/app/navbar/navbar";
import { patch } from "@web/core/utils/patch";
import { useService } from "@web/core/utils/hooks";

patch(Navbar.prototype, {
    setup() {
        super.setup();
        this.quantityService = useService("quantity_service");
    }
});
