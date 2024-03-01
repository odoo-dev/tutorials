/** @odoo-module **/

import { Component, onMounted, onWillUnmount } from "@odoo/owl";
export class UnmountingExample extends Component {
    static template = "awesome_owl.unmounting";

    setup() {

        onMounted(async () => {
            this.timer = setInterval(() => {
                console.log("Demonstration On Mounted");
            }, 1000);
        });

        onWillUnmount(() => {
            console.log("Demonstration UnMounting")
            clearInterval(this.timer);
        });
    }

    updateData() {
        this.state.userInfo = this.ama;
    }
}

