import { NumberCard } from "./number_card/number_card";
import { PieChartCard } from "./pie_chart_card/pie_chart_card";
import { registry } from "@web/core/registry";

const items = [
    {
        id: "average_quantity",
        description: "Average amount of t-shirt",
        Component: NumberCard,
        // size and props are optionals
        size: 3,
        props: (data) => ({
            title: "Average amount of t-shirt by order this month",
            value: data.average_quantity,
        }),
    },
    {
        id: "average_quantity2",
        description: "Average amount of t-shirt",
        Component: NumberCard,
        // size and props are optionals
        size: 1,
        props: (data) => ({
            title: "Test",
            value: data.average_quantity,
        }),
    },
    {
        id: "pie_chart1",
        description: "Some stats",
        Component: PieChartCard,
        size: 2,
        props: (data) => ({
            title: "Test Pie Chart",
            values: data.orders_by_size,
        }),
    },
];

items.forEach((item) => registry.category("awesome_dashboard").add(item.id, item));
