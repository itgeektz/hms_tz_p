# Copyright (c) 2021, Aakvatech and contributors
# For license information, please see license.txt

import frappe
import json
from frappe import bold
from frappe.model.workflow import apply_workflow
from frappe.model.document import Document

class LRPMTReturns(Document):
	def validate(self):
		set_missing_values(self)
	
	def on_submit(self):
		validate_reason(self)
		cancel_lrpt_doc(self)
		return_drug_item(self)

def cancel_lrpt_doc(self):
	for item in self.lrpt_items:
		frappe.db.set_value("Lab Prescription", item.child_name, "is_cancelled", 1)
		frappe.db.set_value("Radiology Procedure Prescription", item.child_name, "is_cancelled", 1)
		frappe.db.set_value("Procedure Prescription", item.child_name, "is_cancelled", 1)
		frappe.db.set_value("Therapy Plan Detail", item.child_name, "is_cancelled", 1)

		doc = frappe.get_doc(item.reference_doctype, item.reference_docname)
		apply_workflow(doc, "Not Serviced")

		if doc.meta.get_field("status"):
			doc.status = "Not Serviced"
			doc.save(ignore_permissions=True)

	return self.name

def return_drug_item(self):
	for item in self.drug_items:
		frappe.db.set_value("Drug Prescription", item.child_name, "is_cancelled", 1)
		
		# doc = frappe.get_doc("Delivery Note", item.delivery_note)
		# if doc.docstatus == 1:
		# 	doc.cancel()
		# 	for drug_item in doc.items:
		# 		if (item.drug_name == drug_item.item_code):
		# 			frappe.db.set_value("Delivery Note Item", drug_item.name, "status", "Not Serviced")
		# 	doc.save(ignore_permissions=True)
		# 	doc.submit()
		# else:
		# 	for drug_item in doc.items:
		# 		if (item.drug_name == drug_item.item_code):
		# 			frappe.db.set_value("Delivery Note Item", drug_item.name, "status", "Not Serviced")
		# 	doc.save(ignore_permissions=True)
	
	return self.name

def validate_reason(self):
	if self.lrpt_items:
		for entry in self.lrpt_items:
			if not entry.reason:
				msg="Reason Field is Empty for Row: #{0}, Please Fill it to proceed"
				frappe.throw(title="Notification", msg=msg.format(bold(entry.idx)), exc="Frappe.ValidationError")
	
	if self.drug_items:
		for entry in self.drug_items:
			if not (entry.reason or entry.drug_condition):
				msg = "Reason or Drug Condition Field is Empty for Row: #{0}, Please Fill It to proceed"
				frappe.throw(title="Notification", msg=msg.format(bold(entry.idx)), exc="Frappe.ValidationError")

@frappe.whitelist()
def get_lrpt_item_list(patient, appointment_no, company):
	item_list = []
	child_list = get_lrpt_map()

	encounter_list = get_patient_encounters(patient, appointment_no, company)

	for child in child_list:
		items = frappe.get_all(child["doctype"], 
			filters={"parent": ["in", encounter_list], "is_not_available_inhouse": 0, "is_cancelled": 0},
			fields=child["fields"]
		)
		
		for item in items:
			if item.lab_test_code:
				item_list.append({
					"child_name": item.name,
					"item_name": item.lab_test_code,
					"quantity": 1,
					"encounter_no": item.parent,
					"reference_doctype": "Lab Test",
					"reference_docname": item.lab_test
				})
			
			if item.radiology_examination_template:
				item_list.append({
					"child_name": item.name,
					"item_name": item.radiology_examination_template,
					"quantity": 1,
					"encounter_no": item.parent,
					"reference_doctype": "Radiology Examination",
					"reference_docname": item.radiology_examination
				})
			
			if item.procedure:
				item_list.append({
					"child_name": item.name,
					"item_name": item.procedure,
					"quantity": 1,
					"encounter_no": item.parent,
					"reference_doctype": "Clinical Procedure",
					"reference_docname": item.clinical_procedure
				})
			
			if item.therapy_type:
				therapy_plan = frappe.get_value("Patient Encounter", item.parent, "therapy_plan")
				item_list.append({
					"child_name": item.name,
					"item_name": item.therapy_type,
					"quantity": 1,
					"encounter_no": item.parent,
					"reference_doctype": "Therapy Plan",
					"reference_docname": therapy_plan
				})
	return item_list

def get_lrpt_map():
	child_map = [
		{
			"doctype": "Lab Prescription",
			"fields": [
				"name",
				"lab_test_code",
				"lab_test_name",
				"lab_test",
				"parent"
			]
		},
		{
			"doctype": "Radiology Procedure Prescription",
			"fields": [
				"name",
				"radiology_examination_template",
				"radiology_procedure_name",
				"radiology_examination",
				"parent"
			]
		},
		{
			"doctype": "Procedure Prescription",
			"fields": [
				"name",
				"procedure",
				"procedure_name",
				"clinical_procedure",
				"parent"
			]
		},
		{
			"doctype": "Therapy Plan Detail",
			"fields": [
				"name",
				"therapy_type",
				"parent"
			]
		}
	]
	return child_map

def set_missing_values(doc):
	appointment_list = frappe.get_all("Patient Appointment", filters={"patient": doc.patient, "status": "Closed"}, 
		fields=["name", "company"], order_by="appointment_date desc", page_length=1
	)

	if appointment_list:
		doc.appointment_no = appointment_list[0]["name"]
		doc.company = appointment_list[0]["company"]

		record = frappe.get_all("Inpatient Record", 
			filters={"patient": doc.patient, "patient_appointment": appointment_list[0]["name"], "status": "Admitted"}, 
			fields=["name", "status", "admitted_datetime"], page_length=1
		)
		if record:
			if (record[0]["name"] and record[0]["status"] and record[0]["admitted_datetime"]):
				doc.inpatient_record = record[0]["name"]
				doc.status = record[0]["status"]
				doc.admitted_datetime = record[0]["admitted_datetime"]
			else:
				pass
	else:
		frappe.throw(
			title='Notification',
			msg='No any Appointment found for this Patient: {0}-{1}'.format(
				frappe.bold(doc.patient),
				frappe.bold(doc.patient_name)
			)
		)

def get_patient_encounters(patient, appointment_no, company):
	if (patient and appointment_no and company):
		conditions = {
			"patient": patient,
			"appointment": appointment_no,
			"company": company,
			"docstatus": 1
		}

		patient_encounter_List = frappe.get_all("Patient Encounter", filters=conditions, 
			fields=["name"], pluck="name", order_by="encounter_date desc"
		)
		return patient_encounter_List

@frappe.whitelist()
def set_checked_lrpt_items(doc, checked_items):
	doc = frappe.get_doc(json.loads(doc))
	checked_items = json.loads(checked_items)
	
	doc.lrpt_items = []
	
	for checked_item in checked_items:
		item_row = doc.append("lrpt_items", {})
		item_row.item_name = checked_item["item"]
		item_row.quantity = checked_item["quantity"]
		item_row.encounter_no = checked_item["encounter"]

		if checked_item["reference_doctype"]:
			item_row.reference_doctype = checked_item["reference_doctype"]

		if checked_item["reference_docname"]:
			item_row.reference_docname = checked_item["reference_docname"]
		
		item_row.child_name = checked_item["child_name"]
	doc.save()
	return doc.name

@frappe.whitelist()
def get_drug_item_list(patient, appointment_no, company):
	drug_list = []
	invoices = []
	delivery_note_items = []

	item_list, name_list, drug_codes = get_drugs(patient, appointment_no, company)
	
	if name_list and drug_codes:
		delivery_note_items += frappe.get_all("Delivery Note Item", filters={"item_code": ["in", drug_codes], 
			"reference_name": ["in", name_list], "reference_doctype": "Drug Prescription"
			}, fields=["parent", "item_code", "reference_name"]
		)

	if name_list:
		sales_invoices = frappe.db.sql("""
			SELECT DISTINCT(sii.parent) FROM `tabSales Invoice Item` sii, `tabSales Invoice` si
			WHERE sii.reference_dn IN {name_list}
			AND sii.reference_dt = "Drug Prescription"
			AND  si.is_pos = 1
		""".format(name_list=tuple(name_list)), as_dict=1)

		if sales_invoices:
			for invoice in sales_invoices:
				invoices.append(invoice["parent"])
	
	if invoices:
		delivery_nos = frappe.get_all("Delivery Note", 
			filters={"form_sales_invoice": ["in", invoices]}, fields=["name"], pluck="name")

		delivery_note_items += frappe.get_all("Delivery Note Item", 
			filters={"parent": ["in", delivery_nos]}, fields=["parent", "item_code", "reference_name"])
	
	for item in item_list:
		for delivery_note in delivery_note_items:
			if (item.drug_code == delivery_note.item_code or item.name == delivery_note.reference_name):
				drug_list.append({
					"child_name": item.name,
					"item_name": item.drug_code,
					"quantity": item.quantity,
					"encounter_no": item.parent,
					"delivery_note": delivery_note.parent
				})
	return drug_list

def get_drugs(patient, appointment_no, company):
	item_list = []
	name_list = []
	drug_code_list = []

	encounter_list = get_patient_encounters(patient, appointment_no, company)
	drugs = frappe.get_all("Drug Prescription", filters={"parent": ["in", encounter_list], "is_not_available_inhouse": 0, "is_cancelled": 0},
		fields=["name", "drug_code", "drug_name", "quantity", "parent"]
	)
	for drug in drugs:
		drug_code_list.append(drug.drug_code)
		name_list.append(drug.name)
		item_list.append(drug)
	
	return item_list, name_list, drug_code_list

@frappe.whitelist()
def set_checked_drug_items(doc, checked_items):
	doc = frappe.get_doc(json.loads(doc))
	checked_items = json.loads(checked_items)
	
	doc.drug_items = []
	
	for checked_item in checked_items:
		item_row = doc.append("drug_items", {})
		item_row.drug_name = checked_item["item_name"]
		item_row.quantity = checked_item["quantity"]
		item_row.encounter_no = checked_item["encounter_no"]

		if checked_item["delivery_note"]:
			item_row.delivery_note_no = checked_item["delivery_note"]
		
		item_row.child_name = checked_item["child_name"]

	doc.save()
	return doc.name


