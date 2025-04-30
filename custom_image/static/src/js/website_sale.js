import { WebsiteSale } from '@website_sale/js/website_sale';


WebsiteSale.include({

    init() {
        this._super(...arguments);
        this.orm = this.bindService("orm");
    },

    async _addToCartInPage(params) {

        const data = await this._super(params);
        console.log(data);
        
        this._uploadCustomImage(data.line_id);

        return data;
    },

    _onConfigured(options, values) {
        
        this._uploadCustomImage(values.line_id);

        return this._super(...arguments);
    },

    async _uploadCustomImage(line_id){
        const fileInput = document.querySelector('input[name="custom_image"]');
        const file = fileInput?.files?.[0];

        if (file && line_id) {
            await new Promise((resolve) => {
                const reader = new FileReader();
                reader.onload = async () => {
                    const base64Image = reader.result.split(',')[1];

                    await this.orm.write('sale.order.line', [line_id], {
                        custom_image: base64Image,
                    });

                    resolve();
                };
                reader.readAsDataURL(file);
            });
        }
        return
    }

});
