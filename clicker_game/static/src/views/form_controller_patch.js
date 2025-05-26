/** @odoo-module **/

import { patch } from "@web/core/utils/patch";
import { FormController } from "@web/views/form/form_controller";
import { getReward } from "../clicker_game/click_rewards"; // import your reward logic
import { useService } from "@web/core/utils/hooks";
import { useClicker } from "../utils"

patch(FormController.prototype, {
    setup() {
        super.setup();
        this.notification = useService("notification");
        this.actionService = useService("action");
        this.clicker = useClicker();
        // Add random chance (1%)
        const chance = Math.random();
        if (chance <= 0.01) {
            // Use reward logic
            this._triggerClickerReward();
        }
    },
        
    async _triggerClickerReward() {
        const reward = getReward(this.clicker.levels.level);
    
        if (!reward) return;
    
        const notif = this.notification.add(`Congrats you won a reward: ${reward.description}`,{
            type: "success",
            sticky: true,
            buttons: [
                {
                    name: "Collect",
                    primary: true,
                    onClick: async () => {
                        reward.apply(this.clicker);
                        this.actionService.doAction({
                            type: "ir.actions.client",
                            tag: "awesome_clicker.client_action",
                            target: "new",
                            name: "Clicker Game"
                        });
                        notif();
                    },
                },
            ],
        });
    }
});
