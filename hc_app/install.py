
import frappe

def after_install():
    default_activities = [
        "Design",
        "Development",
        "Strategy & Research",
        "Project Management",
    ]
    for activity_name in default_activities:
        if not frappe.db.exists(
            "Activity Type",
            {"activity_name": activity_name}
        ):
            frappe.get_doc({
                "doctype": "Activity Type",
                "activity_name": activity_name,
            }).insert(ignore_permissions=True)

    settings = frappe.get_single("Hourcap Settings")
    if not settings.delivery_email:
        settings.delivery_email = "admin@example.com"
    settings.save(ignore_permissions=True)

    frappe.msgprint("HourCap installation setup completed successfully!")
    #print("Function execution completed")
