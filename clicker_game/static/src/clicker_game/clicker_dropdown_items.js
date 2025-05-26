/** @odoo-module **/

import { _t } from "@web/core/l10n/translation";
import { registry } from "@web/core/registry";

function openClickGame(env) {
    return {
        type: "function",
        id: "open",
        description: _t("Open the clicker game"),
        sequence: 10,
    };
}

function buyClickBot(env) {
    return {
        type: "function",
        id: "buyClickBot",
        description: _t("But a ClickBot"),
        sequence: 20,
    };
}

function pearTree(env){
    return {
        type: "Text",
        id: "pearsTree",
        description: "x pearTree",
        sequence: 30,
    }
}

function cherryTree(env){
    return {
        type: "Text",
        id: "cherriesTree",
        description: "x cherryTree",
        sequence: 40,
    }
}

function peachTree(env){
    return {
        type: "Text",
        id: "peachesTree",
        description: "x peachTree",
        sequence: 50,
    }
}

function pearfruit(env){
    return {
        type: "Text",
        id: "pears",
        description: "x pear",
        sequence: 60,
    }
}

function cherryFruit(env){
    return {
        type: "Text",
        id: "cherries",
        description: "x cherry",
        sequence: 70,
    }
}

function peachFruit(env){
    return {
        type: "Text",
        id: "peaches",
        description: "x peach",
        sequence: 80,
    }
}

registry
    .category("clicker_menuitems")
    .add("click_game", openClickGame)
    .add("buy_click_bot", buyClickBot)
    .add("pear_tree", pearTree)
    .add("cherry_tree", cherryTree)
    .add("peach_tree",peachTree)
    .add("pear_fruit", pearfruit)
    .add("cherry_fruit", cherryFruit)
    .add("peach_fruit", peachFruit);
