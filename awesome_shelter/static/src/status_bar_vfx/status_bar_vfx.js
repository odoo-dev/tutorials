import { registry } from "@web/core/registry";
import { useService } from "@web/core/utils/hooks";
import { statusBarField } from "@web/views/fields/statusbar/statusbar_field";


class StatusBarVFX extends statusBarField.component {
    static template = statusBarField.component.template;
    static props = { ...statusBarField.component.props };

    setup() {
        super.setup();
        this.effect_service = useService("effect");
    }

    async selectItem(item) {
        super.selectItem(item);
        if (item.value === 'adopted') {
            this.effect_service.add({ message: `${ this.props.record.data.name } has been adopted` });
        }
    }
}

registry.category("fields").add("status_bar_vfx", {
    ...statusBarField,
    additionalClasses: ["o_field_statusbar"],
    component: StatusBarVFX,
});
