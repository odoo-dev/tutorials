// import { WebsiteSale } from '@website_sale/js/website_sale';
// import { rpc } from "@web/core/network/rpc";

// WebsiteSale.include({
//     init() {
//         this._super.apply(this, arguments);
//     },

//     _onConfigured(options, values) {
//         if (values?.line_id) {
//             this._uploadCustomImage(values.line_id);
//         }
//         return this._super.apply(this, arguments);
//     },

//     async _addToCartInPage(params) {
//         const data = await this._super(params);
//         if (data?.line_id) {
//             await this._uploadCustomImage(data.line_id);
//         }
//         return data;
//     },

//     async _uploadCustomImage(lineId) {
//         const file = document.getElementById('custom_image')?.files?.[0] ?? null;

//         if (file) {
//             const base64Image = await this._base64Formatter(file);
//             await rpc('/shop/upload_custom_image', {
//                 line_id: lineId,
//                 image_base64: base64Image,
//                 filename: file.name,
//                 mimetype: file.type,
//             });
//         }
//     },

//     _base64Formatter(file) {
//         return new Promise((resolve, reject) => {
//             const reader = new FileReader();
//             reader.onload = () => {
//                 const base64 = reader.result?.split(',')[1];
//                 base64 ? resolve(base64) : reject("Invalid base64");
//             };
//             reader.onerror = reject;
//             reader.readAsDataURL(file);
//         });
//     },
// });

import { WebsiteSale } from '@website_sale/js/website_sale';

WebsiteSale.include({
    init() {
        this._super.apply(this, arguments);
        this.orm = this.bindService("orm");
    },

    async _addToCartInPage(params) {
        const data = await this._super(params);
        if (data?.line_id) {
            await this._uploadCustomImage(data.line_id);
        }
        return data;
    },

    _onConfigured(options, values) {
        if (values?.line_id) {
            this._uploadCustomImage(values.line_id);
        }
        return this._super.apply(this, arguments);
    },

    async _uploadCustomImage(lineId) {
        const fileInput = document.getElementById('custom_image');
        const file = fileInput?.files?.[0];
        if (!file) return;

        try {
            const base64Image = await this._base64Formatter(file);

            // await this._createAttachment(base64Image, lineId, file);

            await this.orm.write('sale.order.line', [lineId], {
                custom_image: base64Image,
            });

            console.log('Image uploaded and saved!');
        } catch (error) {
            console.error('Image upload failed:', error);
        }
    },

    _base64Formatter(file) {
        return new Promise((resolve, reject) => {
            const reader = new FileReader();
            reader.onload = () => {
                const base64 = reader.result?.split(',')[1];
                base64 ? resolve(base64) : reject("Invalid base64 result.");
            };
            reader.onerror = reject;
            reader.readAsDataURL(file);
        });
    },

    // async _createAttachment(base64Image, lineId, file) {
    //     const attachmentData = {
    //         name: file.name || 'custom_image',
    //         type: 'binary',
    //         datas: base64Image,
    //         res_model: 'sale.order.line',
    //         res_id: lineId,
    //         store_fname: file.name || 'custom_image.jpg',
    //         mimetype: file.type || 'image/jpeg',
    //     };

    //     const result = await this.orm.call('ir.attachment', 'create', [attachmentData]);
    //     console.log(result);
        
    //     return result;
    // },
});
