
import frappe
from frappe.utils import today
from datetime import datetime


def has_job_run_today():
    last_run = frappe.db.get_value(
        "Audit Log",{
            "action": "retainer_threshold_check",
            "timestamp": [">=", today()]
        }, "name")
    return bool(last_run)


def get_current_month_retainers():
    current_date = datetime.strptime(today(), "%Y-%m-%d")

    current_year = current_date.year
    current_month = current_date.strftime("%b")

    retainers = frappe.get_all(
        "Retainer",
        filters={
            "retainer_year": current_year,
            "retainer_month": current_month
        },
        fields=["name", "client", "total_hours"]
    )

    return retainers


def get_used_hours(retainer_name):
    used_hours = frappe.db.sql("""
        SELECT COALESCE(SUM(total_hours), 0)
        FROM `tabTimesheet`
        WHERE retainer = %s
        AND docstatus = 1
    """, (retainer_name,))[0][0]

    return used_hours


def check_retainer_thresholds():

    if has_job_run_today():
        return

    threshold = frappe.db.get_single_value(
        "Hourcap Settings",
        "low_hours_alert_threshold_percent"
    )

    if threshold is None:
        frappe.log_error(
            "Alert threshold is not configured",
            "Daily Retainer Burn Check"
        )
        return

    retainers = get_current_month_retainers()

    client_names = list({
        r["client"] for r in retainers if r["client"]
    })

    clients = frappe.get_all(
        "Client",
        filters={"name": ["in", client_names]},
        fields=["name", "client_name", "account_manager"]
    ) if client_names else []

    client_map = {c["name"]: c for c in clients}

    manager_names = list({
        c["account_manager"]
        for c in clients
        if c["account_manager"]
    })

    users = frappe.get_all(
        "User",
        filters={"name": ["in", manager_names]},
        fields=["name", "email"]
    ) if manager_names else []

    user_map = {u["name"]: u["email"] for u in users}

    for r in retainers:

        allocated_hours = r["total_hours"] or 0

        if allocated_hours <= 0:
            continue

        used_hours = get_used_hours(r["name"])

        utilization = (used_hours / allocated_hours) * 100

        if utilization >= threshold:

            client = client_map.get(r["client"])

            if not client:
                continue

            account_manager = client["account_manager"]

            recipient = user_map.get(account_manager)

            if not recipient:
                continue

            frappe.sendmail(
                recipients=[recipient],
                subject=f"Retainer Alert: {client['client_name']}",
                message=f"""
                    <p>Hello,</p>

                    <p>The retainer for
                    <b>{client['client_name']}</b>
                    has reached its alert threshold.</p>

                    <p>
                    <b>Retainer:</b> {r['name']}<br>
                    <b>Allocated Hours:</b> {allocated_hours}<br>
                    <b>Used Hours:</b> {used_hours}<br>
                    <b>Utilization:</b> {utilization:.2f}%<br>
                    <b>Alert Threshold:</b> {threshold}%
                    </p>

                    <p>Please review the retainer.</p>
                """
            )

    audit_log = frappe.get_doc({
        "doctype": "Audit Log",
        "doctype_name": "Retainer",
        "document_name": "Daily Retainer Burn Check",
        "action": "retainer_threshold_check",
        "user": frappe.session.user,
        "timestamp": frappe.utils.now_datetime()
    })

    audit_log.insert(ignore_permissions=True)


def print_timesheet_clients():
    timesheets = frappe.get_all(
        "Timesheet",
        fields=["name", "client"]
    )

    client_names = list({
        t["client"] for t in timesheets if t["client"]
    })

    clients = frappe.get_all(
        "Client",
        filters={"name": ["in", client_names]},
        fields=["name", "client_name", "account_manager"]
    ) if client_names else []

    client_map = {
        c["name"]: c for c in clients
    }

    for t in timesheets:

        client = client_map.get(t["client"])

        if client:
            print(
                client["client_name"],
                client["account_manager"]
            )


