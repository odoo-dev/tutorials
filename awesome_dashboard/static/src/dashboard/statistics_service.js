import { rpc } from "@web/core/network/rpc";
import { reactive } from "@odoo/owl"


export const statisticsService = {
    start() {

        const data = reactive({data: {}})

        const loadStatistics = async () => {
            const res = await rpc("/awesome_dashboard/statistics")
            data.data = res
        }

        loadStatistics()

        setInterval(loadStatistics, 10000)
        return { data, loadStatistics }
    }
}
