# Copyright (c) 2013, Aakvatech and contributors
# For license information, please see license.txt

import frappe
from frappe import _, get_cached_value
from frappe.utils import flt, nowdate
from erpnext.accounts.utils import get_balance_on

def execute(filters=None):
	args = frappe._dict(filters or {})
	
	columns = get_columns()
	data = get_data(args)

	report_summary = get_report_summary(args, data)

	return columns, data, None, None, report_summary

def get_columns():
	columns = [
		{"fieldname": "checkin_date", "fieldtype": "Date", "label": _("Checkin Date")},
		{"fieldname": "service_unit", "fieldtype": "Data", "label": _("Service Unit")},
		{"fieldname": "service_unit_type", "fieldtype": "Data", "label": _("Service Unit Type")},
		{"fieldname": "inpatient_charges", "fieldtype": "Currency", "label": _("Inpatient Charges")},
		{"fieldname": "total_lab_amount", "fieldtype": "Currency", "label": _("Lab Amount")},
		{"fieldname": "total_radiology_amount", "fieldtype": "Currency", "label": _("Radiology Amount")},
		{"fieldname": "total_procedure_amount", "fieldtype": "Currency", "label": _("Procedure Amount")},
		{"fieldname": "total_drug_amount", "fieldtype": "Currency", "label": _("Medication Amount")},
		{"fieldname": "total_therapy_amount", "fieldtype": "Currency", "label": _("Therapies Amount")},
		{"fieldname": "grand_total", "fieldtype": "Currency", "label": _("Amount Used Per Day")}
	]
	
	return columns

def get_data(args):
	service_list = []

	service_units = get_inpatient_details(args)
	
	start_date = service_units[0]["check_in"].strftime("%Y-%m-%d")
	end_date = service_units[-1]["check_in"].strftime("%Y-%m-%d")

	encouter_transactions = get_encounter_data(args, start_date, end_date)

	for service in service_units:
		total_amount = total_lab_amount = total_radiology_amount = 0
		total_procedure_amount = total_drug_amount = total_therapy_amount = 0

		checkin_date = service.check_in.strftime("%Y-%m-%d")

		rate = flt(service.rate)
		amount = flt(service.amount)

		for encounter in encouter_transactions:
			encounter_date = encounter["encounter_date"].strftime("%Y-%m-%d")

			if checkin_date == encounter_date:

				total_lab_amount += encounter["lab_amount"]
				total_radiology_amount += encounter["radiology_amount"]
				total_procedure_amount += encounter["procedure_amount"]
				total_drug_amount += encounter["drug_amount"]
				total_therapy_amount += encounter["therapy_amount"]
				total_amount += encounter["total_amount"]
		
		grand_total = total_amount + amount + rate
				
		service_list.append({
			"checkin_date": checkin_date,
			"service_unit": service["service_unit"],
			"service_unit_type": service["service_unit_type"],
			"inpatient_charges": amount + rate,
			"total_lab_amount": total_lab_amount,
			"total_radiology_amount": total_radiology_amount,
			"total_procedure_amount": total_procedure_amount,
			"total_drug_amount": total_drug_amount,
			"total_therapy_amount": total_therapy_amount,
			"grand_total": grand_total
		})

	return service_list

def get_encounter_data(args, start_date, end_date):
	
	encounter_services = []

	encounter_list = frappe.get_all("Patient Encounter", 
		filters=[["patient", "=", args.patient], ["appointment", "=", args.appointment_no], ["company", "=", args.company],
		["inpatient_record", "=", args.inpatient_record], ["encounter_date", "between",  [start_date, end_date]]],
		fields=["name", "encounter_date"], order_by = "encounter_date desc"
	)

	for enc in encounter_list:
		total_amount = lab_amount = radiology_amount = 0
		procedure_amount = drug_amount = therapy_amount = 0

		lab_transactions = frappe.get_all("Lab Prescription", 
			filters={"prescribe": 1, "is_not_available_inhouse": 0, "is_cancelled": 0, "parent": enc.name},
			fields=["amount"]
		)
		 
		for lab in lab_transactions:
			lab_amount += lab.amount

		radiology_transactions = frappe.get_all("Radiology Procedure Prescription",
			filters={"prescribe": 1, "is_not_available_inhouse": 0, "is_cancelled": 0, "parent": enc.name},
			fields=["amount"]
		)
		for radiology in radiology_transactions:
			radiology_amount += radiology.amount

		procedure_transactions = frappe.get_list("Procedure Prescription", 
			filters={"prescribe": 1, "is_not_available_inhouse": 0, "is_cancelled": 0, "parent": enc.name},
			fields=["amount"]
		)
		for procedure in procedure_transactions:
			procedure_amount += procedure.amount

		drug_transactions = frappe.get_all("Drug Prescription", 
			filters={"prescribe": 1, "is_not_available_inhouse": 0, "is_cancelled": 0, "parent": enc.name},
			fields=["quantity", "amount"]
		)
		for drug in drug_transactions:
			amount = drug.quantity * drug.amount
			drug_amount += amount

		therapy_transactions = frappe.get_all("Therapy Plan Detail", 
			filters={"prescribe": 1, "is_not_available_inhouse": 0, "is_cancelled": 0, "parent": enc.name},
			fields=["amount"]
		)
		for therapy in therapy_transactions:
			therapy_amount += therapy.amount
	
		total_amount += lab_amount + radiology_amount + procedure_amount + drug_amount + therapy_amount
		
		encounter_services.append({
			"encounter_date": enc.encounter_date,
			"lab_amount": lab_amount,
			"radiology_amount": radiology_amount,
			"procedure_amount": procedure_amount,
			"drug_amount": drug_amount,
			"therapy_amount": therapy_amount,
			"total_amount": total_amount
		})

	return encounter_services

def get_inpatient_details(args):
	
	parent = args['inpatient_record']

	service_unit_details = frappe.db.sql("""
		SELECT io.service_unit, io.check_in, io.amount, hsu.service_unit_type, ic.rate
		FROM `tabInpatient Occupancy` io
		INNER JOIN `tabHealthcare Service Unit` hsu ON io.service_unit = hsu.name
		LEFT JOIN `tabInpatient Consultancy` ic ON io.parent = ic.parent 
				AND io.check_in = ic.date AND ic.is_confirmed = 1
		WHERE io.is_confirmed = 1
		AND io.parent = %s
		ORDER BY io.check_in asc
	"""%frappe.db.escape(parent), as_dict=1)

	return service_unit_details

def get_patient_balance(args):
	
	customer = frappe.get_value("Patient", {"name": args.patient}, ["customer"])
	start_date = frappe.get_value("Patient Appointment", 
		{"name": args.appointment_no, "patient": args.patient}, ["appointment_date"]
	)
	discharge_date = frappe.get_value("Inpatient Record", {"name": args.inpatient_record}, ["discharge_date"])
	
	if discharge_date:
		end_date = discharge_date
	else:
		end_date = nowdate()

	customer_balances = frappe.get_all("Payment Entry", filters=[
		["party", "=", customer], ["company", "=", args.company],
		["posting_date", "between", [start_date, end_date]] ],
		fields=["name", "paid_amount"]
	)

	balance = 0
	for d in customer_balances:
		balance += d.paid_amount

	return balance

def get_report_summary(args, summary_data):

	balance = get_patient_balance(args)

	total_amount = 0
	for entry in summary_data:
		total_amount += entry["grand_total"]
	
	current_balance = balance - total_amount

	currency = frappe.get_cached_value("Company", args.company, "default_currency")

	return [
		{
			"value": balance,
			"label": _("Total Patient Balance"),
			"datatype": "Currency",
			"currency": currency
		},
		{
			"value": total_amount,
			"label": _("Total Amount Used"),
			"datatype": "Currency",
			"currency": currency
		},
		{
			"value": current_balance,
			"label": _("Current Balance"),
			"datatype": "Currency",
			"currency": currency
		}
	]