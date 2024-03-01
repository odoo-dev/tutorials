/** @odoo-module **/

import { useEffect, useRef } from "@odoo/owl";

// Custom Hook to focus an Input

export function useFocus(name) {
    let ref = useRef(name);
    useEffect(
        (el) => el && el.focus(),
        () => [ref.el]
    );
}


