import { ProductCatalogKanbanModel } from "@product/product_catalog/kanban_model";
import { patch } from "@web/core/utils/patch";
import { rpc } from "@web/core/network/rpc";

patch(ProductCatalogKanbanModel.prototype, {
    async _loadData(params) {
        const result = await super._loadData(...arguments);
        if (!result.records?.length) {
            return result;
        }

        this.records = [...result.records];
        let orderType = params.context.product_catalog_order_model === "purchase.order" ? "purchase" : "sale";
        let partnerId = await this._fetchPartnerId(params);
        if (!partnerId) {
            return result;
        }
        
        let partnerProductData = await this._fetchPartnerProductData(orderType, partnerId);
        const productDates = {};
        partnerProductData.forEach((line) => {
            const productId = line.product_id[0];
            const invoiceDate = line.invoice_date;
            const createDate = line.create_date;            
            if (!productId) return;
            
            if (!productDates[productId]) {
                productDates[productId] = {
                    invoice_date: null,
                    create_date: null
                };
            }            
            if (invoiceDate && (!productDates[productId].invoice_date || 
                new Date(invoiceDate) > new Date(productDates[productId].invoice_date))) {
                productDates[productId].invoice_date = invoiceDate;
                productDates[productId].create_date = createDate;
            }
        });

        this.records.forEach((p) => {
            const dates = productDates[p.id];
            if (dates) {
                p.last_invoice_date = dates.invoice_date ? new Date(dates.invoice_date) : null;
                p.last_create_date = dates.create_date ? new Date(dates.create_date) : null;
                p.primary_sort_date = p.last_invoice_date ? p.last_invoice_date.getTime() : 0;
            } else {
                p.last_invoice_date = null;
                p.last_create_date = null;
                p.primary_sort_date = 0;
            }
        });

        this.records.sort((a, b) => {
            if (a.primary_sort_date !== b.primary_sort_date) {
                return b.primary_sort_date - a.primary_sort_date;
            }
            const aCreateTime = a.last_create_date ? a.last_create_date.getTime() : 0;
            const bCreateTime = b.last_create_date ? b.last_create_date.getTime() : 0;
            return bCreateTime - aCreateTime;
        });        
        return { ...result, records: this.records };
    },

    async _fetchPartnerId(params) {
        if (!params.context.order_id) return null;
        try {
            const orderData = await rpc("/web/dataset/call_kw", {
                model: params.context.product_catalog_order_model,
                method: "read",
                args: [[params.context.order_id], ["partner_id"]],
                kwargs: { context: params.context },
            });
            return orderData?.[0]?.partner_id?.[0] || null;
        } catch (error) {
            console.error("Error fetching order details:", error);
            return null;
        }
    },

    async _fetchPartnerProductData(orderType, partnerId) {
        try {
            const moveType = orderType === "sale" ? 
                ["out_invoice", "out_receipt", "out_refund"] : 
                ["in_invoice", "in_receipt", "in_refund"];
                
            return await rpc("/web/dataset/call_kw", {
                model: "account.move.line",
                method: "search_read",
                args: [
                    [
                        ["move_id.partner_id", "=", partnerId], 
                        ["move_id.move_type", "in", moveType],
                        ["move_id.state", "=", "posted"],
                        ["product_id", "!=", false]
                    ]
                ],
                kwargs: {
                    fields: ["product_id", "move_id", "invoice_date", "create_date"],
                    order: "invoice_date desc, move_id.id desc, id asc",
                    limit: 100,
                },
            });
        } catch (error) {
            console.error("Error fetching partner's product history:", error);
            return [];
        }
    }
});
