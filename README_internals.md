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

