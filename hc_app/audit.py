import frappe 
from frappe.utils import now_datetime


def log_change(doc, method):

        if doc.doctype == "Audit Log":
            return
        action_map = {
            "on_update": "Save",
            "on_submit": "Submit",
            "on_cancel": "Cancel",
        }
        action = action_map.get(method)

        frappe.get_doc({
            "doctype": "Audit Log",
            "doctype_name": doc.doctype,
            "document_name": doc.name,
            "action": action,
            "user": frappe.session.user,
            "timestamp": now_datetime(),
        }).insert(ignore_permissions=True)
