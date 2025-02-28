import { Component } from '@web/core/component'; // <-- Add this import
import publicWidget from '@web/legacy/js/public/public_widget';

publicWidget.registry.WebsiteSale.include({
    _onChangeCombination(ev, $parent, combination) {
        const res = this._super.apply(this, arguments);

        // Update the displayed combination info
        Component.env.bus.trigger('updateCombinationInfo', combination);

        // Get the sell quantity input field
        const $sellQtyInput = $parent.find("input[name='sell_qty']");
        if ($sellQtyInput.length) {
            combination.sell_qty = parseFloat($sellQtyInput.val()) || 1.0;
        }

        return res;
    },

    _onClickSell(ev) {
        ev.preventDefault();

        let $form = $(ev.currentTarget).closest("form");
        let productId = $form.find("input[name='product_id']").val();
        let sellQty = $form.find("input[name='sell_qty']").val();

        // Send the sell request
        this._rpc({
            route: "/shop/cart/update_sell",
            params: {
                product_id: productId,
                sell_qty: sellQty,
            },
        }).then(function () {
            window.location.href = "/shop/cart";
        });
    },
});

// Bind click event to "Sell" button
$(document).on("click", ".js_sell_product", function (ev) {
    publicWidget.registry.WebsiteSale.prototype._onClickSell.call(this, ev);
});
