/** @odoo-module */

import { WebsiteSale } from '@website_sale/js/website_sale';


WebsiteSale.include({
    /**
     * @override
     */

    _updateRootProduct($form, productId, productTemplateId){
        this._super(...arguments);
        const fileInput = $form.find('input[name="custom_image"]')[0];
        const file = fileInput.files[0];
        if(file){
            const reader = new FileReader();
            reader.onload = () => {
                const base64StringCustomImage = reader.result.split(',')[1];
                Object.assign(this.rootProduct, {
                    custom_image: base64StringCustomImage,
                })
            }
            reader.readAsDataURL(file)
        }
    }
})
