import { renderToString } from "@web/core/utils/render";
import { patch } from "@web/core/utils/patch";
import { NameAndSignature } from "@web/core/signature/name_and_signature";

patch(NameAndSignature.prototype, {

    async drawCurrentName() {
        // If the signature type is 'stamp', render the stamp instead of the normal signature
        if(this.props.signatureType === "stamp"){
            const font = this.fonts[this.currentFont];
            const stampData = this.getStampData(); // Get all the user-provided stamp details
            const canvas = this.signatureRef.el;
            const img = this.getSVGStamp(font, stampData, canvas.width, canvas.height);
            await this.printImage(img);
        }
        else{
            super.drawCurrentName()
        }
    },

    // Collect and return stamp details entered by the user
    getStampData() {
        return {
            name: this.props.signature.name,
            company: this.props.signature.company,
            address: this.props.signature.address,
            city: this.props.signature.city,
            country: this.props.signature.country,
            vat: this.props.signature.vat,
            logo: this.props.signature.logo,
        }
    },

    // Generate an SVG string for the stamp and return it as a data URI
    getSVGStamp(font, stampData, width, height){
        const svg = renderToString("sign_stamp.Stamp_SVG", {
            width: width,
            height: height,
            font: font,
            name: stampData.name,
            company: stampData.company,
            address: stampData.address,
            city: stampData.city,
            country: stampData.country,
            vat: stampData.vat,
            logo: stampData.logo
        });
        return "data:image/svg+xml," + encodeURI(svg)
    },

    // Handle input field changes for the stamp (text fields and logo upload)
    onInputData(ev){
        if(ev.target.name === "logo"){
            const file = ev.target.files[0];
            if(file){
                const reader = new FileReader();
                reader.onload = () => {
                    this.props.signature.logo = reader.result;
                    this.drawCurrentName();
                };
                reader.readAsDataURL(file)
            }
        }
        else{
            this.props.signature[ev.target.name] = ev.target.value;
        }
        // Show the signature area if it's currently hidden and we have stamp data
        if(!this.state.showSignatureArea && this.getStampData()){
            this.state.showSignatureArea = true;
        }
        if(this.state.signMode === "auto"){
            this.drawCurrentName();
        }
    },

    setMode(mode, reset){
        super.setMode(mode, reset)
        if(this.props.signatureType === "stamp"){
            this.signaturePad['off']();
        }
    }

})
