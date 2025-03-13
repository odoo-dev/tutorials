import { patch } from "@web/core/utils/patch";
import { RelationalModel } from "@web/model/relational_model/relational_model";
import { getFieldsSpec } from "@web/model/relational_model/utils";
import { orderByToString } from "@web/search/utils/order_by";
import { rpc } from "@web/core/network/rpc";

patch(RelationalModel.prototype, {
    async _loadUngroupedList(config) {
        const orderBy = config.orderBy.filter((o) => o.name !== "__count");

        const allProductIds = await this.orm.search(config.resModel, config.domain, { limit: 0 });

        if (!allProductIds.length) {
            return { records: [], length: 0 };
        }

        if(config.context.order_id && config.context.product_catalog_order_model){
            const orderLinesInfo = await rpc("/product/catalog/order_lines_info", {
                order_id: config.context.order_id,
                product_ids: allProductIds,
                res_model: config.context.product_catalog_order_model,
                child_field: config.context?.child_field,
            });

            allProductIds.sort((a, b) => {
                const isAAdded = orderLinesInfo[a]?.quantity > orderLinesInfo[b]?.quantity ? 1 : 0;
                const isBAdded = orderLinesInfo[b]?.quantity > orderLinesInfo[a]?.quantity ? 1 : 0;
                return isBAdded - isAAdded;
            });

        }
        const paginatedProductIds = allProductIds.slice(config.offset, config.offset + config.limit);

        const kwargs = {
            specification: getFieldsSpec(config.activeFields, config.fields, config.context),
            order: orderByToString(orderBy),
            context: { bin_size: true, ...config.context },
            count_limit: config.countLimit !== Number.MAX_SAFE_INTEGER ? config.countLimit + 1 : undefined,
        };
        const result = await this.orm.webSearchRead(config.resModel, [["id", "in", paginatedProductIds]], kwargs);

        return {
            records: result.records,
            length: allProductIds.length,
        };
    }
})
