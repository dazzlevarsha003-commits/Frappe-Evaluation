// Copyright (c) 2026, Vars and contributors
// For license information, please see license.txt

function fetch_retainer_remaining(frm) {

    if (!frm.doc.retainer) {
        frm.__retainer_remaining_hours = null;
        return;
    }

    const selected_retainer = frm.doc.retainer;

    frappe.call({
        method: "hc_app.hourcap.doctype.timesheet.timesheet.get_retainer_status",
        args: {retainer: selected_retainer},
        callback: function(r) {
            if (frm.doc.retainer !== selected_retainer) {
                return;}
            if (r.message) {
                frm.__retainer_remaining_hours =
                    flt(r.message.remaining_hours);

                frm.set_intro(
                    `Retainer Hours Remaining: ${frm.__retainer_remaining_hours}`,
                    "blue"
                );
            }
        }
    });
}

frappe.ui.form.on("Timesheet", {
    setup(frm) {
        const months = [
            "Jan", "Feb", "Mar", "Apr",
            "May", "Jun", "Jul", "Aug",
            "Sep", "Oct", "Nov", "Dec"
        ];

        const today = new Date();
        const current_year = today.getFullYear();
        const current_month = months[today.getMonth()];

        frm.set_query("retainer", function() {
            return {
                filters: {
                    client: frm.doc.client || "__no_client_selected__",
                    retainer_year: current_year,
                    retainer_month: current_month
                }
            };
        });

    },

    refresh(frm) {
        const status_colors = {
            "Draft" : "grey",
            "Pending Approval": "orange",
            "Approved": "green",
            "Rejected": "red",
            "Invoiced": "blue",
            "Cancelled": "grey"
        }
        
        if(frm.doc.status) {
            frm.dashboard.add_indicator(
                frm.doc.status,
                status_colors[frm.doc.status] || "grey"
            );
        }

        if (frm.doc.retainer) {
            const selected_retainer = frm.doc.retainer;
            frappe.call({
                method: "hc_app.hourcap.doctype.timesheet.timesheet.get_retainer_status",
                args: {retainer: selected_retainer},
                callback: function(r) {
                    if (frm.doc.retainer !== selected_retainer) {
                        return;}
                    if (r.message) {
                        const remaining = r.message.remaining_hours;
                        frm.set_intro(
                            `Retainer Hours Remaining: ${remaining}`,
                            "blue"
                        );
                    }
                }
            });
        } else {
            frm.set_intro("");
        }

        const can_approve =
        frappe.user.has_role("HC Account Manager") ||
        frappe.user.has_role("HC Delivery Head");

        if (
            can_approve &&
            frm.doc.status == "Pending Approval" &&
            !frm.is_new()
        ) {
            frm.add_custom_button("Approve", function() {
                frappe.confirm(
                    "Are you sure you want to approve this Timesheet?",
                    function() {
                        frappe.msgprint("Approval action will be implemented next.");
                    }
                );
            });
        }

        fetch_retainer_remaining(frm);
    }

});



frappe.ui.form.on("Time Log", {
    hours(frm, cdt, cdn) {

        let total = (frm.doc.time_log || []).reduce(
            (sum, row) => sum + flt(row.hours || 0),
            0
        );

        frappe.model.set_value(
            frm.doctype,
            frm.doc.name,
            "total_hours",
            total
        );

        let remaining_hours = frm.__retainer_remaining_hours;

        if (
            remaining_hours !== null &&
            remaining_hours !== undefined &&
            total > remaining_hours
        ) {
            frappe.show_alert({
                message: `Warning: Your Timesheet total (${total} hours) exceeds the remaining Retainer hours (${remaining_hours} hours).`,
                indicator: "orange"
            }, 5);

        }
    }

});
