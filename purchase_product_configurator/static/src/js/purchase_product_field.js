import { _t } from "@web/core/l10n/translation";
import { useEffect } from '@odoo/owl';
import { serializeDateTime } from "@web/core/l10n/dates";
import { x2ManyCommands } from "@web/core/orm_service";
import { registry } from "@web/core/registry";
import { useService } from "@web/core/utils/hooks";
import {
    ProductLabelSectionAndNoteField,
    productLabelSectionAndNoteField,
} from "@account/components/product_label_section_and_note_field/product_label_section_and_note_field";
import { PurchaseProductConfiguratorDialog } from "./purchase_product_configurator_dialog";

async function applyProduct(record, product) {
    const customAttributesCommands = [
        x2ManyCommands.set([]),
    ];
    for (const ptal of product.attribute_lines) {
        const selectedCustomPTAV = ptal.attribute_values.find(
            ptav => ptav.is_custom && ptal.selected_attribute_value_ids.includes(ptav.id)
        );
        if (selectedCustomPTAV) {
            customAttributesCommands.push(
                x2ManyCommands.create(undefined, {
                    custom_product_template_attribute_value_id: [selectedCustomPTAV.id, "we don't care"],
                    custom_value: ptal.customValue,
                })
            );
        };
    }

    const noVariantPTAVIds = product.attribute_lines.filter(
        ptal => ptal.create_variant === "no_variant"
    ).flatMap(ptal => ptal.selected_attribute_value_ids);

    await record._update({
        product_id: [product.id, product.display_name],
        product_qty: product.quantity,
        configurable_product_no_variant_attribute_value_ids: [x2ManyCommands.set(noVariantPTAVIds)],
        configurable_product_custom_attribute_value_ids: customAttributesCommands,
    });
};

export class PurchaseOrderLineProductVariantField extends ProductLabelSectionAndNoteField {
    static template = "purchase.PurchaseProductVariantField";
    static props = {
        ...ProductLabelSectionAndNoteField.props,
        readonlyField: { type: Boolean, optional: true },
    };

    setup() {
        super.setup();
        this.dialog = useService("dialog");
        this.notification = useService("notification");
        this.orm = useService("orm")
        let isMounted = false;
        let isInternalUpdate = false;
        const { updateRecord } = this;
        this.updateRecord = (value) => {
            isInternalUpdate = true;
            return updateRecord.call(this, value);
        };
        useEffect(value => {
            if (!isMounted) {
                isMounted = true;
            }
            else if (value && isInternalUpdate) {
                if (this.relation === "product.template") {
                    this._onProductTemplateUpdate();
                }
            }
            isInternalUpdate = false;
        }, () => [Array.isArray(this.value) && this.value[0]]);
    }

    get productName() {
        if (this.props.name == 'configurable_product_template_id') {
            const product_id_data = this.props.record.data.product_id;
            if (product_id_data && product_id_data[1]) {
                return product_id_data[1].split("\n")[0];
            }
        }
        return super.productName
    }

    get isProductClickable() {
        return (
            this.props.readonlyField ||
            (this.props.record.model.root.activeFields.order_line &&
                this.props.record.model.root._isReadonly("order_line"))
        );
    }

    get hasExternalButton() {
        const res = super.hasExternalButton;
        return res || (!!this.props.record.data[this.props.name] && !this.state.isFloating);
    }
    get isConfigurableTemplate() {
        return this.props.record.data.configurable_is_configurable_product;
    }

    get configurationButtonHelp() {
        return _t("Edit Configuration");
    }

    onEditConfiguration() {
        if (this.isConfigurableTemplate) {
            this._openProductConfigurator(true);
        }
    }

    async _onProductTemplateUpdate() {
        const result = await this.orm.call(
            'product.template',
            'get_single_product_variant',
            [this.props.record.data.configurable_product_template_id[0]]
        );
        if(result && result.product_id) {
            if (this.props.record.data.product_id != result.product_id.id) {
                await this.props.record.update({
                    product_id: [result.product_id, result.product_name],
                });
            }
        } else {
           this._openProductConfigurator();
        }
    }

    async _openProductConfigurator(edit=false) {
        const purchaseOrderRecord = this.props.record.model.root;
        const purchaseOrderLine = this.props.record.data;
        let ptavIds = this._getVariantPtavIds(purchaseOrderLine);
        let customPtavs = [];

        if (edit) {
            ptavIds.push(...this._getNoVariantPtavIds(purchaseOrderLine));
            customPtavs = await this._getCustomPtavs(purchaseOrderLine);
        }
        this.dialog.add(PurchaseProductConfiguratorDialog, {
            productTemplateId: purchaseOrderLine.configurable_product_template_id[0],
            ptavIds: ptavIds,
            customPtavs: customPtavs,
            quantity: purchaseOrderLine.product_qty,
            productUOMId: purchaseOrderLine.product_uom[0],
            companyId: purchaseOrderRecord.data.company_id[0],
            currencyId: purchaseOrderLine.currency_id[0],
            partnerId: purchaseOrderRecord.data.partner_id[0],
            soDate: serializeDateTime(purchaseOrderRecord.data.date_order),
            edit: edit,
            save: async (mainProduct, optionalProducts) => {
                await Promise.all([
                    applyProduct(this.props.record, mainProduct),
                    ...optionalProducts.map(async product => {
                        const line = await purchaseOrderRecord.data.order_line.addNewRecord({
                            position: 'bottom', mode: 'readonly'
                        });
                        await applyProduct(line, product);
                    }),
                ]);
                purchaseOrderRecord.data.order_line.leaveEditMode();
            },
            discard: () => {
                purchaseOrderRecord.data.order_line.delete(this.props.record);
            },
        });
    }

    // Return the PTAV ids of the provided purchase order line.
    _getVariantPtavIds(purchaseOrderLine) {
        return purchaseOrderLine.configurable_product_template_attribute_value_ids.records.map(
            record => record.resId
        );
    }

    // Return the `no_variant` PTAV ids of the provided purchase order line.
    _getNoVariantPtavIds(purchaseOrderLine) {
        return purchaseOrderLine.configurable_product_no_variant_attribute_value_ids.records.map(
            record => record.resId
        );
    }

    // Return the custom PTAVs of the provided purchase order line.
    async _getCustomPtavs(purchaseOrderLine) {
        const customPtavIds = purchaseOrderLine.configurable_product_custom_attribute_value_ids;
        const customPtavs = customPtavIds.records[0]?.isNew
            ? customPtavIds.records.map(record => record.data)
            : customPtavIds.currentIds.length
                ? await this.orm.read(
                    'product.attribute.custom.value',
                    customPtavIds.currentIds,
                    ['custom_product_template_attribute_value_id', 'custom_value'],
                )
                : [];
        return customPtavs.map(customPtav => ({
            id: customPtav.custom_product_template_attribute_value_id[0],
            value: customPtav.custom_value,
        }));
    }
}

export const purchaseOrderLineProductVariantField = {
    ...productLabelSectionAndNoteField,
    component: PurchaseOrderLineProductVariantField,
    extractProps(fieldInfo, dynamicInfo) {
        const props = productLabelSectionAndNoteField.extractProps(...arguments);
        props.readonlyField = dynamicInfo.readonly;
        return props;
    },
};

registry.category("fields").add("pol_product_variant_many2one", purchaseOrderLineProductVariantField);
