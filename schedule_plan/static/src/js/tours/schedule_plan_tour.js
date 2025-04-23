/** @odoo-module */

import { registry } from "@web/core/registry";
import { patch } from "@web/core/utils/patch";
import { _t } from "@web/core/l10n/translation";
import { markup } from "@odoo/owl";


patch(registry.category("web_tour.tours").get("project_tour"), {
    steps() {
        const originalSteps = super.steps();

        const projectCreationStepIndex = originalSteps.findIndex(
            (step) => step.trigger === ".o_kanban_project_tasks .o_column_quick_create .o_kanban_header input"
        );

        originalSteps.splice(projectCreationStepIndex, 0, {
            trigger: 'li a[href="/odoo/project"]',
            content: markup(_t('Navigate to the <b>Projects</b> module to manage schedules efficiently.')),
            tooltipPosition: 'bottom',
            run: "click",
        }, {
            trigger: ".o_status:last",
            content: _t('Check the current status of your project.'),
            tooltipPosition: 'bottom',
            run: "click",
        }, {
            trigger: "span:contains('On Track')",
            content: _t('Move Your Project to On Track.'),
            tooltipPosition: 'left',
            run: "click",
        }, {
            trigger: "#project_gear_icon:last",
            content: _t('Access project settings to configure schedules and other options.'),
            tooltipPosition: 'bottom',
            run: "click",
        }, {
            trigger: "button[data-menu-xmlid='project.menu_project_config']",
            content: markup(_t('Let\'s Create <b>Subject List</b>.')),
            tooltipPosition: 'bottom',
            run: "click",
        }, {
            trigger: "a[data-menu-xmlid='schedule_plan.schedule_plan_menu_subjects']",
            content: _t('Select Subject\'s Menu.'),
            tooltipPosition: 'left',
            run: "click",
        }, {
            trigger: "button.btn.btn-primary.o_list_button_add:contains('New')",
            content: _t('Create a new subject for your Shedule.'),
            tooltipPosition: 'bottom',
            run: "click"
        }, {
            trigger: "div[name=name] input.o_input[type=text]",
            content: _t('Write Subject Name over here.'),
            tooltipPosition: 'bottom',
            run: "edit"
        }, {
            trigger: "div.o_input_dropdown div.dropdown input.o-autocomplete--input.o_input",
            content: _t('Select Faculty.'),
            tooltipPosition: 'bottom',
            run: "click"
        }, {
            trigger: "div.o_input_dropdown:last div.dropdown:last input.o-autocomplete--input.o_input:last",
            content: _t('Select/Create Room.'),
            tooltipPosition: 'bottom',
            run: "edit"
        }, {
            trigger: "button[type=button]:contains('Save')",
            content: markup(_t('Save the <b>Subject List</b>.')),
            tooltipPosition: 'bottom',
            run: "click",
        }, {
            trigger: "a[data-menu-xmlid='project.menu_projects']",
            content: _t('Now Let\'s Move back to Projects'),
            tooltipPosition: 'bottom',
            run: "click",
        }, {
            trigger: "#project_gear_icon:last",
            content: _t('Access project settings to configure schedules and other options.'),
            tooltipPosition: 'bottom',
            run: "click",
        }, {
            trigger: "li a:contains('Timetable Planning')",
            content: markup(_t('Go to <b>Timetable Planning</b> to define Schedule.')),
            tooltipPosition: 'bottom',
            run: "click",
        }, {
            trigger: "td a[role=button]:contains(Add a line)",
            content: _t('Add a new schedule entry for your project.'),
            tooltipPosition: 'bottom',
            run: "click",
        }, {
            trigger: "td[name='working_day']",
            content: _t('Select the working day for this schedule.'),
            tooltipPosition: 'right',
            run: "edit",
        }, {
            trigger: "td[name='subject_ids']",
            content: _t('Choose subjects for this schedule entry.'),
            tooltipPosition: 'right',
            run: "click",
        }, {
            trigger: "input#date_start_0",
            content: _t('Set the starting date for the scheduled task.'),
            tooltipPosition: 'bottom',
            run: "click",
        }, {
            trigger: 'button.o_form_button_save',
            content: _t('Save the Changes.'),
            tooltipPosition: 'bottom',
            run: "click",
        }, {
            trigger: 'button[name="action_schedule_plan"]',
            content: _t('Finalize and save your schedule plan.'),
            tooltipPosition: 'bottom',
            run: "click",
        }, {
            trigger: 'li a[href="/odoo/project"]',
            content: markup(_t('Return to the <b>Projects</b> module to review your updates.')),
            tooltipPosition: 'bottom',
            run: "click",
        }, {
            trigger: '.o_project_kanban_main:last',
            content: _t('View all scheduled projects in the Kanban board.'),
            tooltipPosition: 'bottom',
            run: "click",
        });

        return originalSteps;
    },
});
