import { patch } from "@web/core/utils/patch";
import { Document } from "@sign/components/sign_request/document_signable";

patch(Document.prototype,{
    getDataFromHTML(){
        super.getDataFromHTML();
        const { el: parent } = this.props.parent;
        this.company = parent.querySelector("#o_sign_signer_company_info")?.value;
        this.address = parent.querySelector("#o_sign_signer_address_info")?.value;
        this.city = parent.querySelector("#o_sign_signer_city_info")?.value;
        this.country = parent.querySelector("#o_sign_signer_country_info")?.value;
        this.vat = parent.querySelector("#o_sign_signer_vat_info")?.value;
        this.logo = parent.querySelector("#o_sign_signer_logo_info")?.value;
    },

    get iframeProps() {
        const props = super.iframeProps;
        props.company = this.company;
        props.address = this.address;
        props.city = this.city;
        props.country = this.country;
        props.vat = this.vat;
        props.logo = this.logo;
        return props;
    },
})
