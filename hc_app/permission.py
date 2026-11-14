#import frappe

#def timesheet_query(user):
    #if not user:
        #user = frappe.session.user
    #if user == "Administrator":
       # return ""
   # if "HC Team Member" in frappe.get_roles(user):
        #return f"""`tabTimesheet`.`team_member` = {frappe.db.escape(user)}"""
   # if "HC Account Manager" in frappe.get_roles(user):
       # return f"""`tabTimesheet`.`Client` in (select `name` from `tabClient` where `account_manager` = {frappe.db.escape(user)} ) """
    #return ""


