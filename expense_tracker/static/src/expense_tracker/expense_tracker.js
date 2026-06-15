import {Component, useState} from "@odoo/owl";

export class ExpenseTracker extends Component {
    static template = "expense.ExpenseTracker";

    setup() {
        this.nextId = 1;

        this.state = useState({
            description: "",
            amount: "",
            category: "Food",
            filter: "All",

            expenses: [],
        });
    }

    addExpense() {
        if (!this.state.description || !this.state.amount) {
            console.log("Description and amount are required");
            return;
        }

        this.state.expenses.push({
            id: this.nextId++,
            description: this.state.description,
            amount: Number(this.state.amount),
            category: this.state.category,
        });

        this.state.description = "";
        this.state.amount = "";
        this.state.category = "Food";
    }

    deleteExpense(id) {

        const index = this.state.expenses.findIndex(
            (expense) => expense.id === id
        );
        console.log("index", index);

        if (index >= 0) {
            this.state.expenses.splice(index, 1);
        }
    }

    get filteredExpenses() {
        if (this.state.filter === "All") {
            return this.state.expenses;
        }

        return this.state.expenses.filter(
            (expense) =>
                expense.category ===
                this.state.filter
        );
    }

    get totalAmount() {
        return this.state.expenses.reduce(
            (sum, expense) =>
                sum + expense.amount, 0);
    }

    categoryTotal(category) {
        return this.state.expenses
            .filter(
                (expense) =>
                    expense.category === category
            )
            .reduce(
                (sum, expense) =>
                    sum + expense.amount,
                0
            );
    }
}