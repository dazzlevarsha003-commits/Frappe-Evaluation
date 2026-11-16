import frappe
import frappe.share

@frappe.whitelist()
def share_timesheet(timesheet_name, user_email):
    frappe.share.add("Timesheet", timesheet_name, user_email, read = 1)



@frappe.whitelist()
def get_all_timesheets_unsafe():

    timesheets = frappe.get_all(
        "Timesheet",
        fields=["name"]
    )

    result = []

    for row in timesheets:
        doc = frappe.get_doc("Timesheet", row.name)

        result.append(doc.as_dict())

    return result


@frappe.whitelist()
def get_all_timesheets_safe():

    user = frappe.session.user

    timesheets = frappe.get_list(
        "Timesheet",
        fields=["name", "client"]
    )

    result = []

    for row in timesheets:

        doc = frappe.get_doc("Timesheet", row.name)

        data = doc.as_dict()

        account_manager = frappe.db.get_value(
            "Client",
            row.client,
            "account_manager"
        )

        if account_manager != user:

            for log in data.get("time_log", []):
                log.pop("hours", None)
                log.pop("notes", None)

        result.append(data)

    return result

@frappe.whitelist()
def notify_delivery_of_new_timesheet(timesheet_name):

    frappe.logger().info(
        f"New Timesheet submitted: {timesheet_name}"
    )