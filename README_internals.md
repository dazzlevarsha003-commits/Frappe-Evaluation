#C3 - How does renaming a record name impacts the linked references?

1. frappe.rename_doc("Client", 'b', 'a')  - Changing the client record name from b to a 
2. Verifying the client, retainer and timesheet records after renaming 
  --doc = frappe.get_doc("Client","a")
  --doc.name 
  --'a'
  --doc = frappe.get_doc("Retainer","RET-2026-0001")
  --doc.client
  --'a'
  --doc = frappe.get_doc("Timesheet","TS-2026-00001")
  --doc.client
  --'a'
3. Changing the client record name dynamically changes the retainer and timesheet records fields due to the link datatype reference of client doctyppe to the fields in the retainer and timesheet doctypes.

-----

#D2 - How frappe.get_list and frappe..get_all impacts in the retrieval of data when different users logs in ?

1. frappe.get_all in the unsafe api retrieves all the records and their data bypassing the permission query conditions for all the users.
2. frappe.get_list in the safe api fetches the records and their data according to the given permission query conditions and the whitelisted api. 
   -- When team manager logs in , only the records belong to them has fetched and the hour and notes of the time log are removed.
   -- When account manager logs in , only the records belong to their clients has fetched and the hour and notes of the time log are showed.
   -- When Delivery head logs in , all the records of the timesheet has fetched and the hour and notes of the time log are removed.

-----

#E1 - What happens when self.save id given in on_update?

1. It produces this error - RecursionError: maximum recursion depth exceeded
2. When a document is getting saved --> on_update calls --> self.save() executes on_update again --> it creates a loop, hence the recursion error happens.
3. Correct pattern - if a fieled value need to be changed as a part of saving, validate() or before_save() can be used;
   -- def before_save():
        self.field = "Updated"
Or if a field value need to be updated after submission, db_set() can be used because db_set() updates the field directly in the database without starting the full document save lifecycle again;
   -- def on_update():
        self.db_set(self.field, "Updated")

-----

#E3 - Performance judgement (frappe.get_doc vs frappe.get_value)

1. frappe.get_value is preferred because
frappe.get_doc --> follows all the document lifecycle and permission checks , also loads the whole doocument
frappe.get_value --> retrieves only the required field value from the given record
   -- threshold = frappe.db.get_value("Hourcap Settings", None, "low_hours_alert_threshold_percent")
       print(threshold)
       85.0

-----


