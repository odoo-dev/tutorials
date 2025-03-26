/** @odoo-module **/

import publicWidget from "@web/legacy/js/public/public_widget";
import { _t } from "@web/core/l10n/translation";
import { loadBundle } from "@web/core/assets";
const { DateTime } = luxon;

publicWidget.registry.FullCalendarWidget = publicWidget.Widget.extend({
    selector: "#calendar",
    init: function (parent, options) {
        this._super.apply(this, arguments);
    },
    willStart: async function () {
        await loadBundle("web.fullcalendar_lib");
    },
    start: async function () {
        const rawData = $(".events_fullcalendar_data").attr("value") || "[]";
        try {
            let slotsData = JSON.parse(rawData);
            const userTimeZone = Intl.DateTimeFormat().resolvedOptions().timeZone;
            let noEventsContent = _t("You don't have any Event planned yet.");
            let calendarHeaders = {
                left: 'dayGridMonth,timeGridWeek,listMonth',
                center: 'title',
                right: 'prev,today,next',
            };

            slotsData = slotsData.map(event => ({
                ...event,
                backgroundColor: event.attended ? "#28a745" : "#dc3545",
                start: DateTime.fromISO(event.start, { zone: "utc" }).setZone(userTimeZone).toISO(),
                end: DateTime.fromISO(event.end, { zone: "utc" }).setZone(userTimeZone).toISO(),
            }));

            if (slotsData.length === 0) {
                calendarHeaders = {
                    left: false,
                    center: 'title',
                    right: false,
                };
            }

            this.calendar = new FullCalendar.Calendar(document.querySelector("#calendar"), {
                events: slotsData,
                headerToolbar: calendarHeaders,
                eventTimeFormat: {
                    hour: 'numeric',
                    minute: '2-digit',
                    meridiem: 'long',
                    omitZeroMinute: true,
                },
                buttonText: {
                    today: _t("Today"),
                    dayGridMonth: _t("Month"),
                    timeGridWeek: _t("Week"),
                    listMonth: _t("List"),
                },
                noEventsContent: noEventsContent,
                navLinks: true,
                dayMaxEventRows: 7,
                displayEventEnd: true,
                height: 'auto',
                eventClick: this.onEventClick.bind(this),
            });
            this.calendar.setOption('height', 520);
            this.calendar.render();
        } catch (error) {
            console.error("Invalid JSON format:", error, rawData);
            return;
        }
    },
    formatDateAsBackend: function (date) {
        return DateTime.fromJSDate(date).toLocaleString({
            ...DateTime.DATE_SHORT,
            ...DateTime.TIME_24_SIMPLE,
        });
    },
    onEventClick: function (info) {
        let attendedBadge = $(".o_attended");

        $(".modal-title").text(info.event.title);
        $(".o_start_date").text(this.formatDateAsBackend(info.event.start));
        $(".o_end_date").text(this.formatDateAsBackend(info.event.end));

        $(".o_lecturer").text(info.event.extendedProps.lecturer || "-");

        if (info.event.extendedProps.attended) {
            attendedBadge.text(_t("Attended")).removeClass("bg-danger").addClass("bg-success");
        } else {
            attendedBadge.text(_t("Not Attended")).removeClass("bg-success").addClass("bg-danger");
        }

        $("#fc-event-slot-onclick-modal").modal("show");
    }
});

publicWidget.registry.FullCalendarWidget;
