import { registry } from "@web/core/registry";
import { memoize } from "@web/core/utils/functions"
import { rpc } from "@web/core/network/rpc";


const fetchData = async () => {
    return await rpc('/supplier_portal/companies')
}

const memoizedFetchData = memoize(fetchData);

const myService = {
    dependencies: [],
    start() {
        return {
            getCompanyData: async () => {
                return await memoizedFetchData();
            },
        };

    },

};

registry.category("services").add("loadCompanyData", myService);