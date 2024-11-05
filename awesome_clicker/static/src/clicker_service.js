import { registry } from "@web/core/registry";
import { ClickerModel } from "./clicker_model";
import { browser } from "@web/core/browser/browser";
import { migrate } from "./clicker_migration";


const clickerService = {
    dependencies: ["action", "effect", "notification"],
    start(env, services) {
        const localState = migrate(JSON.parse(browser.localStorage.getItem("clickerState")));
        const model = localState ? ClickerModel.fromJSON(localState): new ClickerModel();

        setInterval(() => {
            browser.localStorage.setItem("clickerState", JSON.stringify(model))
        }, 10000);

        document.addEventListener("click", () => model.addClick(), true);
        setInterval(() => {
            model.tick();
        }, 10000);

        const bus = model.bus;
        bus.addEventListener("UNLOCK", (ev) => {
            services.effect.add({
                message: `You have unlocked ${ev.detail.unlock}`,
                type: "rainbow_man",
            });
        });
        
        bus.addEventListener("REWARD", (ev) => {
            const reward = ev.detail;
            const closeNotification = services.notification.add(
                `Congrats you won a reward: "${reward.description}"`,
                {
                    type: "success",
                    sticky: true,
                    buttons: [
                        {
                            name: "Collect",
                            onClick: () => {
                                reward.apply(model);
                                closeNotification();
                                services.action.doAction({
                                    type: "ir.actions.client",
                                    tag: "awesome_clicker.client_action",
                                    target: "new",
                                    name: "Clicker Game"
                                });
                            },
                        },
                    ],
                }
            );
        })

        return model;
    }
};

registry.category("services").add("awesome_clicker.clicker_service", clickerService);
