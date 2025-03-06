/** @odoo-module **/

import { Component, useState, onWillStart } from "@odoo/owl";
import { useService } from "@web/core/utils/hooks";
import { rpc } from "@web/core/network/rpc";

export class SupplierPortal extends Component {
    static template = "supplier_portal.landing";

    setup() {
        this.state = useState({
            companies: [],
            selectedCompany: null,
            file: null,
        });

        this.service = useService('loadCompanyData')

        onWillStart(async () => {
            const data = await this.service.getCompanyData()
            this.state.companies = data
        })
    }

    onFileChange(ev) {
        const file = ev.target.files[0];
        if (file) {
            const allowedTypes = ["application/pdf", "text/xml"];
            if (!allowedTypes.includes(file.type)) {
                alert("Invalid file type! Please select a PDF or XML file.");
                ev.target.value = "";
                return;
            }
            this.state.file = file;
        }
    }

    onSelect(e) {
        this.state.selectedCompany = e.target.value

    }

    async create_vendor_bill() {
        if (!this.state.selectedCompany) {
            return alert("Please select a company");
        }
        if (!this.state.file) {
            return alert("Please select a file");
        }
        const reader = new FileReader();
        reader.readAsDataURL(this.state.file);
        reader.onload = async () => {
            const fileBase64 = reader.result.split(',')[1];
            await rpc('/supplier_portal/create_vendor_bill', {
                company_id: this.state.selectedCompany,
                file_name: this.state.file.name,
                file_data: fileBase64,
            });
        };
    }

}
