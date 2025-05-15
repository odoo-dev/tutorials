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

    async _uploadCustomImage(lineId) {
        const fileInput = document.getElementById('custom_image');
        const file = fileInput?.files?.[0];
        if (!file) return;

        try {
            const base64Image = await this._base64Formatter(file);

            await this._createAttachment(base64Image, lineId, file);

            console.log('Image uploaded and saved!');

        } catch (error) {
            console.error('Image upload failed:', error);
        }
    },

    async _createAttachment(base64Image, lineId, file) {       
        const attachmentData = {
            name: file.name || 'custom_image',
            type: 'binary',
            datas: base64Image,
            res_model: 'sale.order.line',
            res_id: lineId,
            public: true,
            mimetype: file.type || 'image/jpeg',
        };

        const attachmentId = await this.orm.call('sale.order.line', 'write', [[lineId], { custom_image: base64Image }], { context: { bypass_security: true } });

        return attachmentId;
    }
});
