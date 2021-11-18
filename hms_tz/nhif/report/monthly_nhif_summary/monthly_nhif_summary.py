# Copyright (c) 2013, Aakvatech and contributors
# For license information, please see license.txt

import frappe
from frappe import _

def execute(filters):
	columns = get_columns()
	data = get_data(filters)
	return columns, data

def get_columns():
	columns = [
		{"fieldname": "accreditation_no", "label": _("Accreditation Number"), "fieldtype": "Data"},
		{"fieldname": "facility_name", "label": _("Facility Name"), "fieldtype": "Data"},
		{"fieldname": "address", "label": _("Address"), "fieldtype": "Data"},
		{"fieldname": "region", "label": _("Region"), "fieldtype": "Data"},
		{"fieldname": "district", "label": _("District"), "fieldtype": "Data"},
		{"fieldname": "ownership", "label": _("Facility Ownership"), "fieldtype": "Data"},
		{"fieldname": "facility_code", "label": _("Facility Code"), "fieldtype": "Data"},
		{"fieldname": "male", "label": _("Male"), "fieldtype": "Data"},
		{"fieldname": "female", "label": _("Female"), "fieldtype": "Data"},
		{"fieldname": "amount_claimed", "label": _("Amount Claimed"), "fieldtype": "Currency"},
		{"fieldname": "consultation", "label": _("Consultation"), "fieldtype": "Currency"},
		{"fieldname": "examination", "label": _("Examination"), "fieldtype": "Currency"},
		{"fieldname": "out_patient_charges", "label": _("Out Patient Charges"), "fieldtype": "Currency"},
		{"fieldname": "in_patient_charges", "label": _("In Patient Charges"), "fieldtype": "Currency"}
	]
	return columns

def get_data(filters):
	parent_list = []
	details = []

	male_count = female_count = total_amount = consultation = examination = 0
	total_amount_for_out_patient = total_amount_for_inpatient = 0

	query = frappe.get_all("NHIF Patient Claim", 
			filters=[["docstatus", "=", 1], ["attendance_date", "between", [filters.from_date, filters.to_date]]],
			fields=["*"]
		)

	facility_code = query[0]["facility_code"]
	company_filter = query[0]["company"]
	facility_name = frappe.get_value("Company", company_filter, "parent_company")

	for d in query:
		parent_list.append(d.name)

		if d.gender == "Male":
			male_count += 1
		else:
			female_count += 1

		total_amount += d.total_amount

		if d.patient_type_code == "IN":
			total_amount_for_inpatient += d.total_amount
		else:
			total_amount_for_out_patient += d.total_amount

	items = frappe.get_all("NHIF Patient Claim Item", 
			filters={"docstatus": 1, "parent": ["in", parent_list]},
			fields=["ref_doctype", "amount_claimed"]
		)
	
	for item in items:
		if item.ref_doctype == "Patient Appointment":
			consultation += item.amount_claimed
		else:
			if item.ref_doctype != "Inpatient Occupancy":
				examination += item.amount_claimed
	
	details.append({
		"accreditation_no": "",
		"address": "",
		"region": "",
		"district": "",
		"ownership": "",
		"facility_name": facility_name,
		"facility_code": facility_code,
		"male": male_count,
		"female": female_count,
		"amount_claimed": total_amount,
		"consultation": consultation,
		"examination": examination,
		"out_patient_charges": total_amount_for_out_patient,
		"in_patient_charges": total_amount_for_inpatient
	})
	
	return details