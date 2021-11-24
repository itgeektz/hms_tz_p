# Copyright (c) 2013, Aakvatech and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.utils import getdate

def execute(filters):
	data = []
	columns = get_columns()
	
	nhif_summary = get_data(filters)
	
	company_info = frappe.get_all("Company", 
		filters={"name": nhif_summary[0]["facility_name"]}, 
		fields=["p_o_box", "city"]
	)

	nhif_summary[0]["address"] = company_info[0]["p_o_box"]
	nhif_summary[0]["region"] = company_info[0]["city"]
	nhif_summary[0]["district"] = "Ilala"

	data += nhif_summary

	return columns, data

def get_columns():
	columns = [
		{"fieldname": "male", "label": _("Male"), "fieldtype": "Data"},
		{"fieldname": "female", "label": _("Female"), "fieldtype": "Data"},
		{"fieldname": "amount_claimed", "label": _("Total Amount Claimed"), "fieldtype": "Currency"},
		{"fieldname": "consultation", "label": _("Consultation"), "fieldtype": "Currency"},
		{"fieldname": "diagnostic_examination", "label": _("Diagnostic Examination"), "fieldtype": "Currency"},
		{"fieldname": "surgical_produceral_charge", "label": _("Surgical and Procedural Charges"), "fieldtype": "Currency"},
		{"fieldname": "medicine", "label": _("Medication and Consumables"), "fieldtype": "Currency"},
		{"fieldname": "inpatient_charges", "label": _("Inpatient/Bed Charges"), "fieldtype": "Currency"},
	]
	return columns

def get_data(filters):
	details = []
	parent_list = []

	male_count = female_count = total_amount = total_amount_for_out_patient = total_amount_for_inpatient = 0 
	consultation = diagnostic_examination = surgical_produceral_charge = medicine = inpatient_charges = 0

	nhif_doc = frappe.qb.DocType("NHIF Patient Claim")
	
	claims = (
		frappe.qb.from_(nhif_doc)
		.select(nhif_doc.name, nhif_doc.company, nhif_doc.facility_code, nhif_doc.gender, nhif_doc.total_amount)
		.where(
			(nhif_doc.docstatus == 1)
			& (nhif_doc.company == filters.get("company"))
			& (
				(nhif_doc.attendance_date >= filters.get("from_date")) & (nhif_doc.attendance_date <= filters.get("to_date"))
			)
		)
	).run(as_dict=1)

	facility_code = claims[0]["facility_code"]
	facility_name = claims[0]["company"]

	for claim_doc in claims:
		parent_list.append(claim_doc.name)

		if claim_doc.gender == "Male":
			male_count += 1
		else:
			female_count += 1

		total_amount += claim_doc.total_amount
	
	claim_item = frappe.qb.DocType("NHIF Patient Claim Item")
	items = (
		frappe.qb.from_(claim_item).select(claim_item.ref_doctype, claim_item.amount_claimed).where(
			(claim_item.docstatus == 1) & (claim_item.parent.isin(parent_list))
		)
	).run(as_dict=1)
	
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
		"accreditation_no": "01440",
		"ownership": "Religious/NGO",
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