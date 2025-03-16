import * as ProductScreen from "@point_of_sale/../tests/tours/utils/product_screen_util";
import * as Dialog from "@point_of_sale/../tests/tours/utils/dialog_util";
import * as Chrome from "@point_of_sale/../tests/tours/utils/chrome_util";
import { registry } from "@web/core/registry";

registry.category("web_tour.tours").add("PosAlternativeNameTour", {
    checkDelay: 50,
    steps: () =>
        [
            Chrome.startPoS(),
            Dialog.confirm(),
            ProductScreen.clickDisplayedProduct("Premium Chair"),
            Chrome.endTour(),
        ].flat(),
});

registry.category("web_tour.tours").add("SearchProductsWithAlternativeName", {
    checkDelay: 50,
    steps: () =>
        [
            Chrome.startPoS(),
            ProductScreen.searchProduct("Premium"),
            ProductScreen.clickDisplayedProduct("Premium Chair"),
            ProductScreen.searchProduct("Custom"),
            ProductScreen.clickDisplayedProduct("Custom desk"),
            ProductScreen.searchProduct("prEmiUm"),
            ProductScreen.clickDisplayedProduct("Premium Chair"),
            Chrome.endTour(),
        ].flat(),
});

registry.category("web_tour.tours").add("OrderLinesWithAlternativeName", {
    checkDelay: 50,
    steps: () =>
        [
            Chrome.startPoS(),
            ProductScreen.clickDisplayedProduct("Premium Chair"),
            ProductScreen.selectedOrderlineHas("Premium Chair", "1.0", "37.95"),
            Chrome.endTour()
        ].flat(),
});

registry.category("web_tour.tours").add("PosProductInformation", {
    checkDelay: 50,
    steps: () =>
        [
            Chrome.startPoS(),
            Dialog.confirm(),
            ProductScreen.clickInfoProduct("Premium Chair"),
            {
                trigger: ".section-description:contains('this is the best chair available in the market')"
            },
            {
                trigger: ".alternative-products article.product .product-content .product-name:contains('Custom desk')"
            },
            Chrome.endTour()
        ].flat(),
});

registry.category("web_tour.tours").add("PosProductAvailableQty", {
    checkDelay: 50,
    steps: () =>
        [
            Chrome.startPoS(),
            Dialog.confirm(),
            {
                trigger: "article.product:has(.product-name:contains('Premium Chair')):has(h1:contains('55'))"
            },
            Chrome.endTour()
        ].flat(),
});

registry.category("web_tour.tours").add("PosProductQuantitySyncBtn", {
    checkDelay: 50,
    steps: () =>
        [
            Chrome.startPoS(),
            {
                trigger: ".status-buttons .btn .fa-refresh"
            },
            {
                trigger: "article.product:has(.product-name:contains('Premium Chair')):has(h1:contains('80'))"
            },
            Chrome.endTour()
        ].flat(),
});
