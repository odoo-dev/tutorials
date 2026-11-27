import { Component, Registry, types as t } from "@odoo/owl";
import { NumberCard } from "../number_card/number_card";
import { PieChartCard } from "../piechart_card/piechart_card";


export const dashboardItems = new Registry({
    validation: t.object({
        id: t.string(),
        description: t.string(),
        Component: t.constructor(Component),
        size: t.number().optional(),
        props: t.function().optional(),
    }),
});

dashboardItems.addById({
    id: "pie_chart",
    description: "Pie Chart of amount of t-shirts by size",
    Component: PieChartCard,
    size: 3,
    props: (data) => ({
        title: "Average amount of t-shirts by size",
        values: data.orders_by_size,
    }),
});

dashboardItems.addById({
    id: "average_quantity",
    description: "Average amount of t-shirt",
    Component: NumberCard,
    props: (data) => ({
        title: "Average amount of t-shirt",
        value: data.average_quantity,
    }),
});
dashboardItems.addById({
    id: "average_time",
    description: "Average amount of time",
    Component: NumberCard,
    props: (data) => ({
        title: "Average amount of time",
        value: data.average_time,
    }),
});
dashboardItems.addById({
    id: "nb_new_orders",
    description: "Number of new orders",
    Component: NumberCard,
    props: (data) => ({
        title: "Number of new orders",
        value: data.nb_new_orders,
    }),
});
dashboardItems.addById({
    id: "nb_cancelled_orders",
    description: "Number of cancelled orders",
    Component: NumberCard,
    props: (data) => ({
        title: "Number of cancelled orders",
        value: data.nb_cancelled_orders,
    }),
});
dashboardItems.addById({
    id: "total_amount",
    description: "Total amount of orders",
    Component: NumberCard,
    props: (data) => ({
        title: "Total amount of orders",
        value: data.total_amount,
    }),
});
