# Copyright (c) 2013, Aakvatech and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.utils import getdate

def execute(filters):
	columns = get_columns()
	data = get_data(filters)
	return columns, data

def get_columns():
	columns = [
		{"fieldname": "male", "label": _("Male"), "fieldtype": "Data"},
		{"fieldname": "female", "label": _("Female"), "fieldtype": "Data"},
		{"fieldname": "amount_claimed", "label": _("Amount Claimed"), "fieldtype": "Currency"},
		{"fieldname": "consultation", "label": _("Consultation"), "fieldtype": "Currency"},
		{"fieldname": "diagnostic_examination", "label": _("Diagnostic Examination"), "fieldtype": "Currency"},
		{"fieldname": "surgical_produceral_charge", "label": _("Surgical and Procedural Charges"), "fieldtype": "Currency"},
		{"fieldname": "medicine", "label": _("Medication and Consumables"), "fieldtype": "Currency"},
		{"fieldname": "inpatient_charges", "label": _("Inpatient Charges"), "fieldtype": "Currency"},
		{"fieldname": "total_amount_for_out_patient", "label": _("Total Amount for Outpatient"), "fieldtype": "Currency"},
		{"fieldname": "total_amount_for_inpatient", "label": _("Total Amount for Inpatient"), "fieldtype": "Currency"}
	]
	return columns

def get_data(filters):
	details = []
	parent_list = []

	male_count = female_count = total_amount = total_amount_for_out_patient = total_amount_for_inpatient = 0 
	consultation = diagnostic_examination = surgical_produceral_charge = medicine = inpatient_charges = 0

	claims = frappe.get_all("NHIF Patient Claim", 
			filters=[
				["docstatus", "=", 1],
				["company", "=", filters.company],
				["attendance_date", "between", [filters.from_date, filters.to_date]]
			],
			fields=["*"]
		)

	facility_code = claims[0]["facility_code"]
	facility_name = claims[0]["company"]

	for claim_doc in claims:
		parent_list.append(claim_doc.name)

		if claim_doc.gender == "Male":
			male_count += 1
		else:
			female_count += 1

		total_amount += claim_doc.total_amount

		if claim_doc.patient_type_code == "IN":
			total_amount_for_inpatient += claim_doc.total_amount
		else:
			total_amount_for_out_patient += claim_doc.total_amount

	items = frappe.get_all("NHIF Patient Claim Item", 
			filters={"docstatus": 1, "parent": ["in", parent_list]},
			fields=["ref_doctype", "amount_claimed"]
		)
	
	for item in items:
		if item.ref_doctype == "Patient Appointment":
			consultation += item.amount_claimed
		elif item.ref_doctype == "Drug Prescription":
			medicine += item.amount_claimed
		elif ((item.ref_doctype == "Lab Prescription") | (item.ref_doctype == "Radiology Procedure Prescription")):
			diagnostic_examination += item.amount_claimed
		elif ((item.ref_doctype == "Procedure Prescription") | (item.ref_doctype == "Therapy Plan Detail")):
			surgical_produceral_charge += item.amount_claimed
		else:
			inpatient_charges += item.amount_claimed
	
	from_date = getdate(filters.get("from_date")).strftime("%d-%m-%Y")
	to_date = getdate(filters.get("to_date")).strftime("%d-%m-%Y")
	
	details.append({
		"from_date": from_date,
		"to_date": to_date,
		"accreditation_no": "",
		"address": "",
		"region": "",
		"district": "",
		"ownership": "",
		"facility_name": facility_name,
		"facility_code": facility_code,
		"male": male_count,
		"female": female_count,
		"total_patient": male_count + female_count,
		"amount_claimed": total_amount,
		"consultation": consultation,
		"diagnostic_examination": diagnostic_examination,
		"surgical_produceral_charge": surgical_produceral_charge,
		"medicine": medicine,
		"inpatient_charges": inpatient_charges,
		"total_amount_for_out_patient": total_amount_for_out_patient,
		"total_amount_for_inpatient": total_amount_for_inpatient
	})
	
	return details