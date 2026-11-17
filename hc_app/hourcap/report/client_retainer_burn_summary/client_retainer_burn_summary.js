// Copyright (c) 2026, Vars and contributors
// For license information, please see license.txt

frappe.query_reports["Client Retainer Burn Summary"] = {
	filters: [
		 {
            fieldname: "from_date",
            label: "From Date",
            fieldtype: "Date",
            reqd: 1
        },
        {
            fieldname: "to_date",
            label: "To Date",
            fieldtype: "Date",
            reqd: 1
        },
        {
            fieldname: "client",
            label: "Client",
            fieldtype: "Link",
            options: "Client",
            reqd: 0
        }
	],
};
