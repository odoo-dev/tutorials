/** @odoo-module **/

import { useRef, onMounted } from "@odoo/owl";

export function useAutofocus(ref) {

    const ref = useRef(ref);

    onMounted(() => {
        ref.el.focus();
    })

}
