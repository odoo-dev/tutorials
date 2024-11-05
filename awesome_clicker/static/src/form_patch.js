import { FormController } from "@web/views/form/form_controller";
import { patch } from "@web/core/utils/patch";
import { useClicker } from "./useclicker";

const FormControllerPatch = {
    setup() {
        super.setup(...arguments);
        if (Math.random() < 1) {
            const clicker = useClicker();
            clicker.giveReward();
        }
    },
};

patch(FormController.prototype, FormControllerPatch);