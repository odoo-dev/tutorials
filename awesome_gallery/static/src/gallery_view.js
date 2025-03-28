/** @odoo-module */

// TODO: Begin here!
import {registry} from "@web/core/registry";
import { GalleryController } from "./gallery_controller";

export const GalleryView={
    type: "gallery",
    display_name: "Gallery",
    icon: "oi oi-view-gallery",
    multiRecord: true,
    Controller: GalleryController
};

registry.category("views").add("gallery", GalleryView);
console.log("XXXXXXXXXXXXXXXXXXXXX\n", registry.category("views"));