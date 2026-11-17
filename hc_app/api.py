import frappe
import frappe.share
from frappe.query_builder import DocType
from frappe.query_builder import Order

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


@frappe.whitelist()
def get_retainer_status(retainer_name=None):

    retainer_name = frappe.form_dict.get("retainer_name")

    purchased = frappe.db.get_value(
        "Retainer",
        retainer_name,
        "total_hours"
    )

    if purchased is None:
        frappe.local.response["http_status_code"] = 404
        return {"error": "Not found"}

    if not frappe.has_permission(
        "Retainer",
        "read",
        doc=retainer_name
    ):
        frappe.throw("Not permitted", frappe.PermissionError)

    result = frappe.db.sql("""
        SELECT COALESCE(SUM(total_hours), 0) AS used
        FROM `tabTimesheet`
        WHERE retainer = %s
        AND docstatus = 1
    """, (retainer_name,), as_dict=True)

    used = result[0]["used"] or 0

    purchased = float(purchased)
    used = float(used)
    remaining = purchased - used

    utilization_percent = (
        (used / purchased) * 100 if purchased > 0 else 0
    )
    return {
        "purchased": purchased,
        "used": used,
        "remaining": remaining,
        "utilization_percent": round(utilization_percent, 2)
    }


def get_timesheets_pending_approval():

    TS = DocType("Timesheet")
    result = (frappe.qb.from_(TS).select(
            TS.name,TS.team_member,TS.client,TS.total_hours,TS.work_date
        )
        .where(TS.status == "Pending Approval")
        .orderby(TS.work_date, order=Order.asc)
        .run(as_dict=True)
    )
    return result
