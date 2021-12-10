import frappe
from frappe.model.document import Document

class LimitChangeRequest(Document):
	def validate(self):
		update_fields(self)
	
	def on_submit(self):
		if self.inpatient_record:
			frappe.db.set_value("Inpatient Record", self.inpatient_record, "cash_limit", self.cash_limit)
			
			inpatient_record_doc = frappe.get_doc("Inpatient Record", self.inpatient_record)

			if inpatient_record_doc.cash_limit == self.cash_limit:
				frappe.msgprint("Inpatient Record: {0} of Patient {1} - {2} has been updated with new cash limit: {3}".format(
					frappe.bold(self.inpatient_record),
					frappe.bold(self.patient),
					frappe.bold(self.patient_name),
					frappe.bold(self.cash_limit)
				))

	def on_cancel(self):
		old_cash_limit = frappe.get_value("Patient", {"name": self.patient}, "cash_limit")
		frappe.db.set_value("Inpatient Record", self.inpatient_record, "cash_limit", old_cash_limit)



def update_fields(self):
	conditions = {}
	if self.patient:
		conditions["patient"] = self.patient
		conditions["docstatus"] = 1
	
	if self.company:
		conditions["company"] = self.company
		
	encounters = frappe.get_all("Patient Encounter", 
		filters=conditions, fields=["name", "encounter_date", "appointment", "inpatient_record"], order_by = "encounter_date desc"
	)

	self.appointment_no = encounters[0]["appointment"]
	self.inpatient_record = encounters[0]["inpatient_record"]



