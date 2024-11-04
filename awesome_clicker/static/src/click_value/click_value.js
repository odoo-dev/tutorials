/** @odoo-module **/

import {Component, useState} from "@odoo/owl";
import {humanNumber} from "@web/core/utils/numbers";
import {useClicker} from "../clicker_hook";


export class ClickerValue extends Component {
    static template = "awesome_clicker.ClickerValue";
    static props = {};

    setup() {
        this.clicker = useClicker();
    }

    get humanValueClicks() {
        return humanNumber(this.clicker.clicks, {decimals: 2});
    }
}
