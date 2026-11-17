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

#I1 - Parameterized SQL vs f-string 

1. f-string SQL 

client = "ABC Company"
query = f"""
    SELECT name, team_member, client, total_hours, work_date
    FROM `tabTimesheet`
    WHERE status = 'Pending Approval'
    AND client = '{client}'
"""
--> Directly inserts Python variable values into SQL. Vulnerable to SQL injection ( ex : client = " ' or 1=1 --") when user input is involved. 

2. Parameterized SQL

select name, team_member, client, total_hours, work_date, status
from `tabTimesheet`
where status = 'Pending Approval'
and (
    %(client)s is null
    or %(client)s = ''
    or client = %(client)s
)
order by work_date desc 
--> Uses named placeholders (%(client)s) for dynamic values. Values are passed separately and safely bound by the database driver. Prevents SQL injection through parameter binding. Supports optional filters without dynamically constructing SQL.

-----

#L1 - REST API

1. REQUEST:
curl -G "http://localhost:8000/api/resource/Timesheet" \
-u "API_KEY:API_SECRET" \
--data-urlencode 'fields=["name","client","total_hours"]'

--->Using built-in REST APIs for DocTypes - Tested the Timesheet read operation using curl.

2. RESPONSE: 
{"data":[{"name":"TS-2026-00002","client":"Orbit Fitness","total_hours":0.0},{"name":"TS-2026-00003","client":"Paperkite Books","total_hours":0.0},{"name":"TS-2026-00004","client":"Tessel Bank","total_hours":0.0},{"name":"TS-2026-00005","client":"Halden Foods","total_hours":21.0},{"name":"TS-2026-00006","client":"Halden Foods","total_hours":5.0},{"name":"TS-2026-00008","client":"Halden Foods","total_hours":1.0},{"name":"TS-2026-00009","client":"Halden Foods","total_hours":1.0},{"name":"TS-2026-00010","client":"Halden Foods","total_hours":1.0},{"name":"TS-2026-00011","client":"Orbit Fitness","total_hours":3.0},{"name":"TS-2026-00012","client":"Orbit Fitness","total_hours":4.0},{"name":"TS-2026-00013","client":"Orbit Fitness","total_hours":3.0},{"name":"TS-2026-00014","client":"Orbit Fitness","total_hours":1.0},{"name":"TS-2026-00015","client":"Paperkite Books","total_hours":2.0},{"name":"TS-2026-00016","client":"Paperkite Books","total_hours":2.0},{"name":"TS-2026-00017","client":"Tessel Bank","total_hours":10.0},{"name":"TS-2026-00018","client":"Orbit Fitness","total_hours":4.0},{"name":"TS-2026-00019","client":"Halden Foods","total_hours":6.0},{"name":"TS-2026-00020","client":"Orbit Fitness","total_hours":5.0},{"name":"TS-2026-00021","client":"Paperkite Books","total_hours":31.0},{"name":"TS-2026-00022","client":"Tessel Bank","total_hours":38.0}]}

--> JSON output of the twenty records for the requested fields

#CUSTOM WHITELISTED FUNCTION 

1. Test result of whitelisted API function

COMMAND:
curl -G "http://localhost:8000/api/method/hc_app.api.get_retainer_status" \
-u "a72872efacdf966:40c2909cd48e4c8" \
--data-urlencode "retainer_name=RET-2026-0001"
RESULT:
{"message":{"purchased":30.0,"used":27.0,"remaining":3.0,"utilization_percent":90.0}}

2. 404 Error test

COMMAND:
curl -i -G "http://localhost:8000/api/method/hc_app.api.get_retainer_status" \
-u "a72872efacdf966:40c2909cd48e4c8" \
--data-urlencode "retainer_name=INVALID-RETAINER"
RESULT:
HTTP/1.1 404 NOT FOUND
Server: Werkzeug/3.1.9 Python/3.14.6
Date: Tue, 17 Nov 2026 14:17:38 GMT
Content-Type: application/json
Content-Length: 33
Cache-Control: no-store,no-cache,must-revalidate,max-age=0
Set-Cookie: sid=Guest; Expires=Tue, 24 Nov 2026 16:17:38 GMT; Max-Age=612000; HttpOnly; Path=/; SameSite=Lax
Set-Cookie: system_user=no; Path=/; SameSite=Lax
Set-Cookie: full_name=Guest; Path=/; SameSite=Lax
Set-Cookie: user_id=Guest; Path=/; SameSite=Lax
Set-Cookie: user_lang=en; Path=/; SameSite=Lax
Connection: close

{"message":{"error":"Not found"}}



