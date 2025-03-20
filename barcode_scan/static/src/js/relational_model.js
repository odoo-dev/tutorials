import { patch } from "@web/core/utils/patch";
import { RelationalModel } from "@web/model/relational_model/relational_model";
import { getFieldsSpec } from "@web/model/relational_model/utils";
import { orderByToString } from "@web/search/utils/order_by";
import { rpc } from "@web/core/network/rpc";

patch(RelationalModel.prototype, {
    async _loadUngroupedList(config) {
        const orderBy = config.orderBy.filter((o) => o.name !== "__count");

        const allProductIds = await this.orm.search(config.resModel, config.domain);

        if (!allProductIds.length) {
            return { records: [], length: 0 };
        }

        let orderLinesInfo = {};
        if (config.context.order_id && config.context.product_catalog_order_model) {
            orderLinesInfo = await rpc("/product/catalog/order_lines_info", {
                order_id: config.context.order_id,
                product_ids: allProductIds,
                res_model: config.context.product_catalog_order_model,
            });

            allProductIds.sort((a, b) => (orderLinesInfo[b]?.quantity || 0) - (orderLinesInfo[a]?.quantity || 0));
        }

        const paginatedProductIds = allProductIds.slice(config.offset, config.offset + config.limit);

        const kwargs = {
            specification: getFieldsSpec(config.activeFields, config.fields, config.context),
            order: orderByToString(orderBy),
            context: { bin_size: true, ...config.context },
            count_limit: config.countLimit !== Number.MAX_SAFE_INTEGER ? config.countLimit + 1 : undefined,
        };

        const result = await this.orm.webSearchRead(config.resModel, [["id", "in", paginatedProductIds]], kwargs);

        result.records.sort((a, b) => (orderLinesInfo[b.id]?.quantity || 0) - (orderLinesInfo[a.id]?.quantity || 0));

        return {
            records: result.records,
            length: allProductIds.length,
        };
    }
});
