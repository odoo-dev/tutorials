/** @odoo-module **/

import {useService} from "@web/core/utils/hooks";
import {useState} from "@odoo/owl";

export function useClicker() {
    return useState(useService("clicker_service"));
}