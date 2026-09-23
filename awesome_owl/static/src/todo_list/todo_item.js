import { Component, useState, xml } from "@odoo/owl";

export class TodoItem extends Component {
    static template = "awesome_owl.todo.item";
    static props = {
        todo : {
            id : {type : Number},
            description : {type : String},
            isCompleted : {type : Boolean},
        }
    }


    get id() {return this.props.id}
}