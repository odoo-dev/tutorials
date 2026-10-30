import { Component, useProps, t, onMounted, onWillUnmount, signal } from "@odoo/owl";


export class Timer extends Component {
    static template = "tutorial.timer"
    
    value = signal(0)
    props = useProps({increment: t.number()})

    setup() {
        let intervalId;

        onMounted(() => {
            intervalId = setInterval(
                () => this.value.set(this.value() + this.props.increment)
            ), 1000
        });
        onWillUnmount(() => {
            clearInterval(intervalId);
        });
    }
}
