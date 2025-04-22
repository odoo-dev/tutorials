import { Document } from "@sign/components/sign_request/document_signable";
import { patch } from "@web/core/utils/patch";


patch(Document.prototype, {
    getDataFromHTML(){
        super.getDataFromHTML()
        const { el: parentEl } = this.props.parent;

        // Getting values from sign_request_templates.xml
        this.company = parentEl.querySelector("#o_sign_signer_company_input_info")?.value;
        this.address = parentEl.querySelector("#o_sign_signer_address_input_info")?.value;
        this.city = parentEl.querySelector("#o_sign_signer_city_input_info")?.value;
        this.country = parentEl.querySelector("#o_sign_signer_country_input_info")?.value;
        this.vat = parentEl.querySelector("#o_sign_signer_vat_input_info")?.value;
        this.logo = parentEl.querySelector("#o_sign_signer_logo_input_info")?.value;

    },

    get iframeProps(){
        return{
            ...super.iframeProps,
            company: this.company,
            address: this.address,
            city: this.city,
            country: this.country,
            vat: this.vat,
            logo: this.logo,
        }
    },

})
