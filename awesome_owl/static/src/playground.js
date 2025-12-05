import { Component, useState } from "@odoo/owl";
import {Counter} from "./Counter/counter";
import {Card} from "./Card/card";
import {TodoList} from "./Todo/todo";

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
