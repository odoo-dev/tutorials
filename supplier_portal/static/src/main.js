import { whenReady } from "@odoo/owl";
import { mountComponent } from "@web/env";
import { SupplierPortal } from "./supplier_portal";


const config = {
    dev: true,
    name: "Supplier Portal",
};

whenReady(() => mountComponent(SupplierPortal, document.body, config));
