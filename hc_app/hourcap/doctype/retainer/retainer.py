# Copyright (c) 2026, Vars and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document

 
class Retainer(Document):
	
	def validate(self):
		if self.total_hours <= 0:
			frappe.throw("Total Hours must be greater than zero")

		if frappe.db.exists(
		"Retainer",
		{
			"client": self.client,
			"retainer_year": self.retainer_year,
			"retainer_month": self.retainer_month
		}):
			frappe.throw("A Retainer already exists for this Client, Year and Month")
