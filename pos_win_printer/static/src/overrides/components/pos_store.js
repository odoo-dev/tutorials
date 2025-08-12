/** @odoo-module **/

import { patch } from "@web/core/utils/patch";
import { PosStore } from "@point_of_sale/app/store/pos_store";
import { OrderReceipt } from "@point_of_sale/app/screens/receipt_screen/receipt/order_receipt";
import { toPng } from "@point_of_sale/app/utils/html-to-image";
import { loadAllImages } from "@point_of_sale/utils";

patch(PosStore.prototype, {

    async printReceipt({
        basic = false,
        order = this.get_order()
    } = {}) {
        try {
            if (!window?.printerAPI?.printReceipt) {
                console.log("printerAPI not available, using default receipt printing");
                return await super.printReceipt?.(...arguments) ?? true;
            }

            const rendererService = this.env?.services?.renderer;
            if (!rendererService) {
                console.warn("Renderer service not available");
                return await super.printReceipt?.(...arguments) ?? true;
            }

            const rendererProps = {
                data: this.orderExportForPrinting(order),
                formatCurrency: this.env?.utils?.formatCurrency ?? ((v) => v),
                basic_receipt: basic,
            };

            let el = document.querySelector(".pos-receipt");

            if (!el) {
                try {
                    el = await rendererService.toHtml(OrderReceipt, rendererProps);
                } catch (renderErr) {
                    console.warn("Could not render receipt HTML", renderErr);
                    return await super.printReceipt?.(...arguments) ?? true;
                }
            }

            if (!el) {
                console.warn("No receipt element available");
                return await super.printReceipt?.(...arguments) ?? true;
            }

            try {
                console.log("Loading all images in receipt...");
                await loadAllImages(el);
                console.log("All images loaded successfully");
            } catch (imageLoadError) {
                console.error("Some images could not be loaded correctly:", imageLoadError);
            }

            const imageOptions = {
                backgroundColor: "#ffffff",
                cacheBust: true,
                pixelRatio: 4,
                useCORS: true,
                allowTaint: true,
                style: {
                    color: "#000000",
                    fontWeight: "bold",
                    fontSize: "16px",
                    lineHeight: "1.2",
                },
            };

            let base64Image;
            try {
                console.log("el", el);
                console.log("imageOptions", imageOptions);


                console.log("Converting receipt to PNG with loaded images...");
                base64Image = await toPng(el, imageOptions);
                console.log("Receipt converted to PNG successfully");
            } catch (imgErr) {
                console.error("Error converting receipt to PNG:", imgErr);
                return await super.printReceipt?.(...arguments) ?? true;
            }

            if (!base64Image) {
                console.warn("Generated receipt image is empty");
                return await super.printReceipt?.(...arguments) ?? true;
            }

            if (window?.printerAPI?.printReceipt) {
                try {
                    console.log("Sending receipt to printer...");
                    await window.printerAPI.printReceipt(base64Image);
                    console.log("Receipt sent to printer successfully");
                } catch (printErr) {
                    console.error("Error sending receipt to printerAPI:", printErr);
                    return await super.printReceipt?.(...arguments) ?? true;
                }
            } else {
                console.warn("printerAPI not available");
                return await super.printReceipt?.(...arguments) ?? true;
            }

            return true;

        } catch (err) {
            console.error("Unexpected error in printReceipt:", err);
            return await super.printReceipt?.(...arguments) ?? true;
        }
    },
});
