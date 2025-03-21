import { renderToString } from "@web/core/utils/render";
import { patch } from "@web/core/utils/patch";
import { NameAndSignature } from "@web/core/signature/name_and_signature";
import { useState } from "@odoo/owl";

patch(NameAndSignature.prototype, {

    async drawCurrentName() {
        if (this.props.signatureType === "stamp") {
            const selectedFont = this.fonts[this.currentFont];
            const stampInfo = this.collectStampData();
            const canvas = this.signatureRef.el;
            const svgImage = this.generateSVGStamp(selectedFont, stampInfo, canvas.width, canvas.height);
            await this.printImage(svgImage);
        } else {
            super.drawCurrentName();
        }
    },

    collectStampData() {
        return {
            name: this.props.signature.name,
            company: this.props.signature.company,
            address: this.props.signature.address,
            city: this.props.signature.city,
            country: this.props.signature.country,
            vat: this.props.signature.vat,
            logo: this.props.signature.logo,
        };
    },

    generateSVGStamp(font, data, width, height) {
        const svgContent = renderToString("sign_stamp.sign_svg_stamp", {
            width,
            height,
            font,
            name: data.name,
            company: data.company,
            address: data.address,
            city: data.city,
            country: data.country,
            vat: data.vat,
            color: this.props.fontColor,
            logo: data.logo,
        });
        return "data:image/svg+xml," + encodeURI(svgContent);
    },

    onInputData(event) {
        const { name, files, value } = event.target;

        if (name === "logo") {
            const file = files[0];
            if (file) {
                const reader = new FileReader();
                reader.onload = () => {
                    this.props.signature.logo = reader.result;
                    this.drawCurrentName();
                };
                reader.readAsDataURL(file);
            }
        } else {
            this.props.signature[name] = value;
        }

        if (!this.state.showSignatureArea && this.collectStampData()) {
            this.state.showSignatureArea = true;
        }

        if (this.state.signMode === "auto") {
            this.drawCurrentName();
        }
    },
});
