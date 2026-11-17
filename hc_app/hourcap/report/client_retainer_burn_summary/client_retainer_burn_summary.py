
# Copyright (c) 2026, Vars and contributors
# For license information, please see license.txt

import frappe
from frappe.utils import getdate, add_months


def execute(filters=None):
    filters = filters or {}

    columns = get_columns()
    data = get_data(filters)

    chart = get_chart(data)
    report_summary = get_report_summary(data)

    return columns, data, None, chart, report_summary


def get_columns():
    return [
        {
            "fieldname": "client",
            "label": "Client",
            "fieldtype": "Link",
            "options": "Client",
            "width": 180
        },
        {
            "fieldname": "hours_purchased",
            "label": "Hours Purchased",
            "fieldtype": "Float",
            "width": 130
        },
        {
            "fieldname": "hours_used",
            "label": "Hours Used",
            "fieldtype": "Float",
            "width": 120
        },
        {
            "fieldname": "hours_remaining",
            "label": "Hours Remaining",
            "fieldtype": "Float",
            "width": 130
        },
        {
            "fieldname": "utilization",
            "label": "Utilization %",
            "fieldtype": "Percent",
            "width": 120
        },
        {
            "fieldname": "timesheet_count",
            "label": "Timesheet Count",
            "fieldtype": "Int",
            "width": 120
        }
    ]


def get_month_number(month):
    months = {
        "Jan": 1,
        "Feb": 2,
        "Mar": 3,
        "Apr": 4,
        "May": 5,
        "Jun": 6,
        "Jul": 7,
        "Aug": 8,
        "Sep": 9,
        "Oct": 10,
        "Nov": 11,
        "Dec": 12
    }

    return months.get(month)


def get_used_hours(filters):
    from_date = getdate(filters.get("from_date"))
    to_date = getdate(filters.get("to_date"))

    timesheet_filters = {
        "docstatus": 1,
        "work_date": ["between", [from_date, to_date]]
    }

    if filters.get("client"):
        timesheet_filters["client"] = filters.get("client")

    timesheets = frappe.get_list(
        "Timesheet",
        fields=["name", "client", "total_hours"],
        filters=timesheet_filters,
        limit_page_length=5000
    )

    used = {}
    counts = {}

    for ts in timesheets:
        client = ts.client

        used[client] = (
            used.get(client, 0) + (ts.total_hours or 0)
        )

        counts[client] = counts.get(client, 0) + 1

    return used, counts


def get_purchased_hours(filters):
    from_date = getdate(filters.get("from_date"))
    to_date = getdate(filters.get("to_date"))

    retainer_filters = {
        "retainer_year": [
            "between",
            [from_date.year, to_date.year]
        ]
    }

    if filters.get("client"):
        retainer_filters["client"] = filters.get("client")

    retainers = frappe.get_list(
        "Retainer",
        fields=[
            "client",
            "retainer_year",
            "retainer_month",
            "total_hours"
        ],
        filters=retainer_filters,
        limit_page_length=5000
    )

    purchased = {}

    for retainer in retainers:
        month = get_month_number(retainer.retainer_month)

        if not month:
            continue

        period_start = getdate(
            f"{retainer.retainer_year}-{month:02d}-01"
        )

        period_end = add_months(period_start, 1)

        # Include the full monthly retainer if its month
        # overlaps the selected report date range.
        if period_start <= to_date and period_end > from_date:
            client = retainer.client

            purchased[client] = (
                purchased.get(client, 0)
                + (retainer.total_hours or 0)
            )

    return purchased


def get_data(filters):
    purchased = get_purchased_hours(filters)
    used, counts = get_used_hours(filters)

    clients = sorted(set(purchased) | set(used))

    data = []

    for client in clients:
        hours_purchased = purchased.get(client, 0)
        hours_used = used.get(client, 0)

        hours_remaining = hours_purchased - hours_used

        utilization = (
            (hours_used / hours_purchased) * 100
            if hours_purchased
            else 0
        )

        timesheet_count = counts.get(client, 0)

        data.append([
            client,
            hours_purchased,
            hours_used,
            hours_remaining,
            utilization,
            timesheet_count
        ])

    return data


def get_chart(data):
    labels = [row[0] for row in data]

    purchased = [row[1] for row in data]
    used = [row[2] for row in data]

    return {
        "data": {
            "labels": labels,
            "datasets": [
                {
                    "name": "Purchased",
                    "values": purchased
                },
                {
                    "name": "Used",
                    "values": used
                }
            ]
        },
        "type": "bar"
    }


def get_report_summary(data):
    total_purchased = sum(
        row[1] for row in data
    )

    total_used = sum(
        row[2] for row in data
    )

    clients_over_85 = sum(
        1 for row in data
        if row[4] > 85
    )

    return [
        {
            "label": "Total Hours Purchased",
            "value": total_purchased,
            "datatype": "Float",
            "indicator": "Blue"
        },
        {
            "label": "Total Hours Used",
            "value": total_used,
            "datatype": "Float",
            "indicator": "Green"
        },
        {
            "label": "Clients Over 85%",
            "value": clients_over_85,
            "datatype": "Int",
            "indicator": "Orange"
        }
    ]
