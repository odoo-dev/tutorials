import { patch } from "@web/core/utils/patch";
import { ProductCatalogKanbanModel } from "@product/product_catalog/kanban_model"
import { rpc } from "@web/core/network/rpc";

patch(ProductCatalogKanbanModel.prototype, {
    async _loadData(params) {
        const result = await super._loadData(...arguments);
        if (!params.isMonoRecord && !params.groupBy.length) {
            const orderLinesInfo = await rpc("/product/catalog/order_lines_info", this._getOrderLinesInfoParams(params, result.records.map((rec) => rec.id)));
            for (const record of result.records) {
                record.productCatalogData = orderLinesInfo[record.id];
            }
        }

        result.records.sort((a, b) => {
            const isAAdded = a.productCatalogData?.quantity > b.productCatalogData?.quantity ? 1 : 0;
            const isBAdded = b.productCatalogData?.quantity > a.productCatalogData?.quantity ? 1 : 0;
            return isBAdded - isAAdded;
        });

        return result;
    }
})
