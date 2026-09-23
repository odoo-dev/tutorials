import { Component, useState, xml } from "@odoo/owl";
import { TodoItem } from "./todo_item";

export class TodoList extends Component {
    static template = "awesome_owl.todo.list";
    static components = { TodoItem };
    // static props = {
    //     todos : { 
    //         type : Array, 
    //         element : {
    //             type : Object,
    //             shape : {
    //                 id : {type : Number},
    //                 description : {type : String},
    //                 isCompleted : {type : Boolean},
    //             }
    //         }
    //     }
    // }
    setup() {
        this.todos = useState([
            { id: 3, description: "buy milk", isCompleted: false },
            { id: 4, description: "buy machin", isCompleted: false },
            { id: 5, description: "buy bidule", isCompleted: false }]);
        console.info(this);
    }
}