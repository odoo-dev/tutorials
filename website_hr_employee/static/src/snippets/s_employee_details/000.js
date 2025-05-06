import publicWidget from "@web/legacy/js/public/public_widget";
import { renderToElement } from "@web/core/utils/render";

publicWidget.registry.employeeDetails = publicWidget.Widget.extend({
    selector : ".s_employee_details",
    disabledInEditableMode: false,

    init(parent, options) {
        this._super.apply(this, arguments);
        this.orm = this.bindService("orm");
    },
    async willStart() {
        const departmentId = parseInt(this.el.dataset.departmentId);
        let domain = [];
        if (departmentId) {
            domain.push(["department_id", "=", departmentId]);
        }
        this.result = await this.orm.searchRead(
            "hr.employee",
            domain,
            ["name", "department_id", "job_id", "work_email", "image_1920"]
        );
    },
    async start() {
        if (this.result) {
            this.el.innerHTML = "";
            const layout = this.el.dataset.layout || "card";
            this.el.append(renderToElement(
                layout === "card" ? "website_hr_employee.s_employee_details_dynamic_card" : "website_hr_employee.s_employee_details_dynamic_list",
                { records: this.result }
            ));
        }
    },
});
