import { FormController } from "@web/views/form/form_controller";
import { patch } from "@web/core/utils/patch";
import { useClicker } from "../clicker_hook";

const FormControllerPatch = {
    setup() {
        super.setup(...arguments);
        const clicker = useClicker();
        console.log("Reward ?")
        const random = Math.random;
        if (Math.random() < 0.05){
            console.log("Reward granted");
            clicker.getReward();
        }
    },
};

patch(FormController.prototype, FormControllerPatch);
