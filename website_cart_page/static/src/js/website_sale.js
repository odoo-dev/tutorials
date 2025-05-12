import { WebsiteSale } from '@website_sale/js/website_sale';

WebsiteSale.include({

    init() {
        this._super.apply(this, arguments);
        this.orm = this.bindService("orm");
    },

    _onConfigured(options, values) {        

        if (values?.line_id) {
            this._uploadCustomImage(values.line_id);
        }

        return this._super.apply(this, arguments);
    },

    async _addToCartInPage(params) {
        const data = await this._super(params);

        if (data?.line_id) {
            await this._uploadCustomImage(data.line_id);
        }

        return data;
    },

    async _uploadCustomImage(lineId) {
        const file = document.getElementById('custom_image')?.files?.[0] ?? null;

            if (file){
                const base64Image = await this._base64Formatter(file);

                await this.orm.write('sale.order.line', [lineId], {
                    custom_image: base64Image,
                    // custom_image_base64: base64Image,
                });
            }
        },

        _base64Formatter(file) {
        return new Promise((resolve, reject) => {
            const reader = new FileReader();

            reader.onload = () => {
                const base64 = reader.result?.split(',')[1];

                if (base64) {
                    resolve(base64);
                } else {
                    reject("Failed to parse base64 from result.");
                }
            };

            reader.readAsDataURL(file);
        });
    },
});
