/** @odoo-module **/
import { ProductScreen } from "@point_of_sale/app/screens/product_screen/product_screen";
import { patch } from "@web/core/utils/patch";

patch(ProductScreen.prototype, {
	getNumpadButtons() {
		const buttons = super.getNumpadButtons(...arguments);

		const deleteLineButton = {
			value: "DeleteLine",
			text: "DEL",
			class: "o_colorlist_item_color_transparent_1",
		};

		const backspaceIndex = buttons.findIndex(
			(button) => button.value === "Backspace"
		);

		if (backspaceIndex > -1) {
			buttons.splice(backspaceIndex, 1, deleteLineButton);
		} else {
			buttons.push(deleteLineButton);
		}

		return buttons;
	},

	onNumpadClick(buttonValue) {
		if (buttonValue === "DeleteLine") {
			this.numberBuffer.sendKey("Backspace");
			this.numberBuffer.sendKey("Backspace");
		} else {
			super.onNumpadClick(...arguments);
		}
	},
});
