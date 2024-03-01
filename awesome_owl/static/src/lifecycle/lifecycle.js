/** @odoo-module **/

import { Component, onPatched, onError, useState, onWillUnmount, useEffect, onMounted, onWillRender, onRendered, onWillStart } from "@odoo/owl";

export class Lifecycle extends Component {

    static template = "awesome_owl.lifecycle";

    setup() {
        this.state = useState({
            userInfo: {
                title: "Dummy",
                brand: "Dummy",
                category: "Dummy",
                price: 0,
                thumbnail: "https://www.birdnote.org/sites/default/files/Great-Horned-Owl-Tucson-800-Mick-Thompson-CC.jpg",
            },
        });

        onWillStart(async () => {
            console.log("On Will Start");
        });

        onWillRender(() => {
            console.log("On Will Render");
        }
        );

        onRendered(() => {
            console.log("On Rendered");
        });

        onPatched(() => {
            console.log("On Patched");
        });

        onMounted(async () => {
            console.log("On Mounted")
            const data = await fetch("https://dummyjson.com/products/2");
            const json = await data.json();
            this.ama = json;
        });

        // onError(() => {
        //     console.log("Some Error");
        // });
    }

    updateData() {
        this.state.userInfo = this.ama;
    }
}

