import { useRef, onMounted } from "@odoo/owl";

/**
 *
 * @param {string} ref
 */
export function useAutofocus(ref) {
	let inputRef = useRef(ref);
	onMounted(() => {
		inputRef.el.focus();
	});
}
