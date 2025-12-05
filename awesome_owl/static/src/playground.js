import { Component, useState } from "@odoo/owl";
import {Counter} from "./components/Counter/counter";
import {Card} from "./components/Card/card";
import {TodoList} from "./components/Todo/todo";

export class Playground extends Component {
    static template = "awesome_owl.playground";
    static components = { Counter, Card, TodoList };

    setup(){
        this.state = useState({value: 0});
    }

    incrementSum(){
        this.state.value++;
    }
}
