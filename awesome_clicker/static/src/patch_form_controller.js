import { useClicker } from "./clicker_hook";
import { useService } from "@web/core/utils/hooks";
import { FormController } from "@web/views/form/form_controller";
import { patch } from "@web/core/utils/patch";

patch(FormController.prototype, {
  setup() {
    this.clicker = useClicker();
    this.notification = useService("notification");
    this.action = useService("action");
    let chance = Math.random();
    if (chance < 0.91) {
      const reward = this.clicker.getReward();
      console.log(reward);
      this.closeFn = this.notification.add(
        `Congrats you won a reward: ${reward.description}`,
        {
          sticky: true,
          type: "success",
          buttons: [
            {
              name: "Collect",
              onClick: () => {
                reward.apply(this.clicker);
                this.action.doAction({
                  type: "ir.actions.client",
                  tag: "awesome_clicker.client_action",
                  target: "new",
                  name: "Clicker Game",
                });
                this.closeFn();
              },
            },
          ],
        }
      );
    }
    super.setup(...arguments);
  },
});