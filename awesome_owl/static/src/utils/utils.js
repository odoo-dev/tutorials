import {onMounted, useRef} from "@odoo/owl";

export function useAutofocus(name) {
    let ref = useRef('todo_desc')
    onMounted(() => {
        ref.el.focus();
    })
}