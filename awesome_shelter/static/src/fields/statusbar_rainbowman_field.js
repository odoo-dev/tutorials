import { registry } from "@web/core/registry"
import { useService } from "@web/core/utils/hooks";
import { statusBarField } from "@web/views/fields/statusbar/statusbar_field";

class StatusbarRainbowManField extends statusBarField.component {
    static template = statusBarField.component.template;
    static props = {
        ...statusBarField.component.props,
        rainbowStages: { type: Array },
    };

    setup() {
        super.setup();
        this.effect = useService("effect");
    }

    async selectItem(item) {
        super.selectItem(item);
        if (this.props.rainbowStages.includes(item.value)) {
            this.effect.add({ message: "A new happy life on the making" });
        }
    }

}

const statusbarRainbowManField = {
    ...statusBarField,
    component: StatusbarRainbowManField,
    extractProps({ options }) {
        const props = statusBarField.extractProps(...arguments);
        props.rainbowStages = options.rainbow_stages;
        return props;
    },
};

registry.category("fields").add("statusbar_rainbowman", statusbarRainbowManField);
