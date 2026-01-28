import { registry } from "@web/core/registry";
import { charField } from "@web/views/fields/char/char_field";


const NAMES = [
    "Alpha",
    "Bravo",
    "Charlie",
    "Delta",
    "Echo",
    "Foxtrot",
];

class NameGenerator extends charField.component {
    static templates = "awesome_shelter.NameGenerator";
    static props = { ...charField.component.props };

    generateName() {
        const random_name = NAMES[Math.floor(Math.random() * NAMES.length)];
        this.props.record.update({ [this.props.name]: random_name });
    }
}

registry.category("fields").add("name_generator", { ...charField, component: NameGenerator });
