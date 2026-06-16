import { Component, useState } from "@odoo/owl";

export class Expense extends Component {
    static template = "awesome_owl.Expense";

    setup() {
        this.state = useState({
            description: "",
            amount: "",
            category: "Food",
            expenses: [],
            filterCategory: "Food",
        });
    }

    addExpense() {
        this.state.expenses.push({
            description:this.state.description,
            amount: Number(this.state.amount),
            category: this.state.category,
        });

        console.log(this.state.expenses);

        this.state.description="";
        this.state.amount="";
        this.state.category="Food";
    }

    getCategoryTotal(category) {
        let total = 0;

        for (const expense of this.state.expenses) {
            if (expense.category === category) {
                total += expense.amount;
            }
        }

        return total;
    }

    getTotalExpense() {
        let total = 0;

        for (const expense of this.state.expenses) {
            total += expense.amount;
        }

        return total;
    }

    getFilteredTotal() {
        let total = 0;

        for (const expense of this.state.expenses) {
            if (expense.category === this.state.filterCategory) {
                total += expense.amount;
            }
        }

        return total;
    }

}