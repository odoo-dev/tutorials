/** @odoo-module **/

import { useEnv } from "@odoo/owl"

export function useCustomEnv() {
    const env = useEnv();
    env.prop1 = 'Dheeraj'; // Change prop1 value
    env.prop2 = 'Pandey'; // Change prop2 value
};
