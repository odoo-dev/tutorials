/** @odoo-module **/
import { Component, useState, useEffect, onWillUnmount, onMounted, useRef, onRendered } from "@odoo/owl";
import { useFocus } from "../focushook/useFocus";
export class UseEffectExample extends Component {

    static template = "awesome_owl.useEffect";
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
        onRendered(() => {
            console.log("UseEffectExample Rendered");
        })

        useEffect(() => {
            this.timer = setInterval(() => {
                console.log("UseEffect On Mounted");
            }, 1000);
        }
,
         () => []);

        onWillUnmount(() => {
            // clearInterval(this.intervalId);
            // console.log("Componnet Unmounting");
        })
    }

    updateData() {
        this.state.userInfo = this.ama;
    }
}