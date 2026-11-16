# Copyright (c) 2026, Vars and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class Timesheet(Document):

    def validate(self):

        total = 0

        for row in self.time_log:
            if row.hours <= 0:
                frappe.throw(
                    f"Hours must be greater than zero in row {row.idx}"
                )

            total += row.hours

        self.total_hours = total

        retainer_client = frappe.db.get_value(
            "Retainer",
            self.retainer,
            "client"
        )

        if retainer_client != self.client:
            frappe.throw(
                "The Timesheet client must match the linked Retainer client"
            )

    
    def before_submit(self):

        retainer = frappe.db.get_value(
            "Retainer",
            self.retainer,
            ["total_hours", "client"],
            as_dict=True
        )

        hours_used_so_far = frappe.db.sql("""
            SELECT COALESCE(SUM(total_hours), 0)
            FROM `tabTimesheet`
            WHERE retainer = %s
            AND docstatus = 1
            AND name != %s
        """, (self.retainer, self.name or ""))[0][0]

        remaining_hours = retainer.total_hours - hours_used_so_far

        if self.total_hours > remaining_hours:

            excess_hours = self.total_hours - remaining_hours

            frappe.throw(
                f"Cannot submit Timesheet for {retainer.client}. "
                f"You are exceeding the Retainer allocation by "
                f"{excess_hours:g} hours. "
                f"Only {remaining_hours:g} hours actually remain."
            )

    

    def on_submit(self):

        retainer = frappe.db.get_value(
            "Retainer",
            self.retainer,
            ["total_hours", "client"],
            as_dict=True
        )

        hours_used_so_far = frappe.db.sql("""
            SELECT COALESCE(SUM(total_hours), 0)
            FROM `tabTimesheet`
            WHERE retainer = %s
            AND docstatus = 1
            AND name != %s
        """, (self.retainer, self.name))[0][0]

        remaining = (
            retainer.total_hours
            - hours_used_so_far
            - self.total_hours
        )

        self.db_set("remaining_hours_at_submission", remaining)

        if not self.approved_by:
            self.db_set("approved_by", frappe.session.user)

        frappe.enqueue(
            "hc_app.hourcap.api.notify_delivery_of_new_timesheet",
            queue="short",
            timesheet_name=self.name
        )

    
    def on_cancel(self):

        if self.status == "Invoiced":
            frappe.throw(
                "Cannot cancel this Timesheet because it has already been Invoiced. "
                "Please process a credit note instead."
            )

        self.db_set("status", "Cancelled")

    
    def on_trash(self):

        if self.status not in ("Cancelled", "Draft"):
            frappe.throw(
                "Only Draft or Cancelled Timesheets can be deleted."
            )

    #def on_update(self):
        #self.save()


