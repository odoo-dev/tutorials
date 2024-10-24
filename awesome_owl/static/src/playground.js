/** @odoo-module **/

import { Component, useState, xml } from "@odoo/owl";
import Counter from "./counter/counter"
import Card from "./card/card"
import TodoList from "./todolist/todolist"

export class Playground extends Component {
    static template = xml`
        <div>
            <div class="card-body">
                <Counter onChange.bind="increment"/>
                <Counter onChange.bind="increment"/>
                <p>
                    Counter: <t t-esc="state.value"/>
                </p>
            </div>
        </div>
        <div>
            <div class="card d-inline-block m-2">
                <div class="card-body">
                    <Card title="'CARD 1'" text="'Text Card 1'"/>
                    <Card title="'CARD 2'" text="'Text Card 2'"/>
                </div>
            </div>
        </div>
        <div>
            <div class="card d-inline-block m-2">
                <div class="card-body">
                    <TodoList/>
                </div>
            </div>
        </div>`;

    static components = {Counter, Card, TodoList}

    setup() {
        this.state = useState({ value: 0 });
    }

    increment() {
        this.state.value++;
    }
}
