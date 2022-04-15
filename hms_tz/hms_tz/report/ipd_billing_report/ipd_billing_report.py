import frappe
from frappe import _, get_cached_value
from frappe.utils import flt, nowdate, getdate
from erpnext.accounts.utils import get_balance_on

def execute(filters=None):
	args = frappe._dict(filters or {})
	
	columns = get_columns()
	data, dashboard = get_data(args)

	return columns, data, None, None, dashboard

def get_columns():
	columns = [
		{"fieldname": "date", "fieldtype": "date", "label": _("Date"), "width": 120},
		{"fieldname": "service_unit", "fieldtype": "Data", "label": _("Service Unit"), "width": 120},
		{"fieldname": "total_bed_charges", "fieldtype": "Currency", "label": _("Bed Charges"), "width": 120},
		{"fieldname": "total_cons_charges", "fieldtype": "Currency", "label": _("Consultation Charges"), "width": 120},
		{"fieldname": "total_lab_amount", "fieldtype": "Currency", "label": _("Lab Amount"), "width": 120},
		{"fieldname": "total_radiology_amount", "fieldtype": "Currency", "label": _("Radiology Amount"), "width": 120},
		{"fieldname": "total_procedure_amount", "fieldtype": "Currency", "label": _("Procedure Amount"), "width": 120},
		{"fieldname": "total_drug_amount", "fieldtype": "Currency", "label": _("Medication Amount"), "width": 120},
		{"fieldname": "total_therapy_amount", "fieldtype": "Currency", "label": _("Therapies Amount"), "width": 120},
		{"fieldname": "grand_total", "fieldtype": "Currency", "label": _("Amount Used Per Day"), "width": 120}
	]
	
	return columns

def get_data(args):
	service_list = []
	date_list = []
	single_transaction_per_day = []
	mult_transaction_per_day = []
	transactions = get_transaction_data(args)
	for record in transactions:
		total_amount = flt(record['bed_charges']) + flt(record['cons_charges']) + flt(record['lab_amount']) +\
				flt(record['radiology_amount']) + flt(record['procedure_amount']) + flt(record['drug_amount']) +\
					flt(record['therapy_amount'])
		
		date_d = record['date'].strftime('%Y-%m-%d')
		if date_d not in date_list:
			date_list.append(date_d)
			record.update({'total_amount': total_amount})
			single_transaction_per_day.append(record)
		else:
			record.update({'total_amount': total_amount})
			mult_transaction_per_day.append(record)
	
	for single_transaction in single_transaction_per_day:
		service_unit = ""
		mult_bed_charges = mult_cons_charges = mult_lab_amount = mult_radiology_amount =\
			mult_procedure_amount = mult_drug_amount = mult_therapy_amount = mult_total_amount = 0
		
		single_transaction_date = single_transaction['date'].strftime('%Y-%m-%d')
		
		for mult_transaction in mult_transaction_per_day:
			mult_transaction_date = mult_transaction['date'].strftime('%Y-%m-%d')

			if single_transaction_date == mult_transaction_date:
				mult_bed_charges += flt(mult_transaction['bed_charges'])
				mult_cons_charges += flt(mult_transaction['cons_charges'])
				mult_lab_amount += flt(mult_transaction['lab_amount'])
				mult_radiology_amount += flt(mult_transaction['radiology_amount'])
				mult_procedure_amount += flt(mult_transaction['procedure_amount'])
				mult_drug_amount += flt(mult_transaction['drug_amount'])
				mult_therapy_amount += flt(mult_transaction['therapy_amount'])
				mult_total_amount += flt(mult_transaction['total_amount'])

				service_unit += mult_transaction['service_unit']
		
		service_list.append({
			'date': single_transaction_date,
			'service_unit': single_transaction['service_unit'] or service_unit,
			'total_bed_charges': flt(single_transaction['bed_charges']) + mult_bed_charges,
			'total_cons_charges': flt(single_transaction['cons_charges']) + mult_cons_charges,
			'total_lab_amount': flt(single_transaction['lab_amount']) + mult_lab_amount,
			'total_radiology_amount': flt(single_transaction['radiology_amount']) + mult_radiology_amount,
			'total_procedure_amount': flt(single_transaction['procedure_amount']) + mult_procedure_amount,
			'total_drug_amount': flt(single_transaction['drug_amount']) + mult_drug_amount,
			'total_therapy_amount': flt(single_transaction['therapy_amount']) + mult_therapy_amount,
			'grand_total': flt(single_transaction['total_amount']) + mult_total_amount
		})
	
	return get_last_row(args, service_list)

def get_transaction_data(args):
	services = frappe.db.sql("""
		select sum(lrpmt.amount) as lab_amount, 0 as radiology_amount, 0 as procedure_amount, 0 as drug_amount,
			0 as therapy_amount, date(pe.encounter_date) as date, "" as service_unit,
			0 as bed_charges, 0 as cons_charges
		from `tabLab Prescription` lrpmt
		inner join `tabPatient Encounter` pe on lrpmt.parent = pe.name
		where pe.inpatient_record = %(inpatient_record)s
		and pe.appointment = %(appointment_no)s
		and pe.patient = %(patient)s
		and pe.company = %(company)s
		and pe.docstatus = 1
		and lrpmt.prescribe = 1
		and lrpmt.is_not_available_inhouse = 0
		and lrpmt.is_cancelled = 0
		and lrpmt.invoiced = 0
		group by pe.encounter_date

		union all

		select 0 as lab_amount, sum(lrpmt.amount) as radiology_amount, 0 as procedure_amount, 0 as drug_amount,
			0 as therapy_amount, date(pe.encounter_date) as date, "" as service_unit,
			0 as bed_charges, 0 as cons_charges
		from `tabRadiology Procedure Prescription` lrpmt
		inner join `tabPatient Encounter` pe on lrpmt.parent = pe.name
		where pe.inpatient_record = %(inpatient_record)s
		and pe.appointment = %(appointment_no)s
		and pe.patient = %(patient)s
		and pe.company = %(company)s
		and pe.docstatus = 1
		and lrpmt.prescribe = 1
		and lrpmt.is_not_available_inhouse = 0
		and lrpmt.is_cancelled = 0
		and lrpmt.invoiced = 0
		group by pe.encounter_date

		union all

		select 0 as lab_amount, 0 as radiology_amount, sum(lrpmt.amount) as procedure_amount,
			0 as drug_amount, 0 as therapy_amount, date(pe.encounter_date) as date, "" as service_unit,
			0 as bed_charges, 0 as cons_charges
		from `tabProcedure Prescription` lrpmt
		inner join `tabPatient Encounter` pe on lrpmt.parent = pe.name
		where pe.inpatient_record = %(inpatient_record)s
		and pe.appointment = %(appointment_no)s
		and pe.patient = %(patient)s
		and pe.company = %(company)s
		and pe.docstatus = 1
		and lrpmt.prescribe = 1
		and lrpmt.is_not_available_inhouse = 0
		and lrpmt.is_cancelled = 0
		and lrpmt.invoiced = 0
		group by pe.encounter_date
		
		union all

		select 0 as lab_amount, 0 as radiology_amount, 0 as procedure_amount,
			sum(lrpmt.amount * (lrpmt.quantity - lrpmt.quantity_returned)) as drug_amount,
			0 as therapy_amount, date(pe.encounter_date) as date, "" as service_unit,
			0 as bed_charges, 0 as cons_charges
		from `tabDrug Prescription` lrpmt
		inner join `tabPatient Encounter` pe on lrpmt.parent = pe.name
		where pe.inpatient_record = %(inpatient_record)s
		and pe.appointment = %(appointment_no)s
		and pe.patient = %(patient)s
		and pe.company = %(company)s
		and pe.docstatus = 1
		and lrpmt.prescribe = 1
		and lrpmt.is_not_available_inhouse = 0
		and lrpmt.is_cancelled = 0
		and lrpmt.invoiced = 0
		group by pe.encounter_date

		union all

		select 0 as lab_amount, 0 as radiology_amount, 0 as procedure_amount, 0 as drug_amount,
			sum(lrpmt.amount) as therapy_amount, date(pe.encounter_date) as date, "" as service_unit,
			0 as bed_charges, 0 as cons_charges
		from `tabTherapy Plan Detail` lrpmt
		inner join `tabPatient Encounter` pe on lrpmt.parent = pe.name
		where pe.inpatient_record = %(inpatient_record)s
		and pe.appointment = %(appointment_no)s
		and pe.patient = %(patient)s
		and pe.company = %(company)s
		and pe.docstatus = 1
		and lrpmt.prescribe = 1
		and lrpmt.is_not_available_inhouse = 0
		and lrpmt.is_cancelled = 0
		and lrpmt.invoiced = 0
		group by pe.encounter_date

		union all

		select 0 as lab_amount, 0 as radiology_amount, 0 as procedure_amount, 0 as drug_amount,
			0 as therapy_amount, date(ipd.check_in) AS date, ipd.service_unit as service_unit, 
			sum(ipd.amount) as bed_charges, 0 as cons_charges
        from `tabInpatient Occupancy` ipd
        where ipd.is_confirmed = 1
		and ipd.invoiced = 0
        and ipd.parent = %(inpatient_record)s
		group by date(ipd.check_in)

		union all

		select 0 as lab_amount, 0 as radiology_amount, 0 as procedure_amount, 0 as drug_amount,
			0 as therapy_amount, date(ipd.date) AS date, "" as service_unit, 
			0 as bed_charges, sum(ipd.rate) as cons_charges
		from `tabInpatient Consultancy` ipd
		where ipd.is_confirmed = 1
		and ipd.hms_tz_invoiced = 0
        and ipd.parent = %(inpatient_record)s
		group by date(ipd.date)
	""", args, as_dict=True)

	return services

def get_report_summary(args, summary_data):
	customer = frappe.get_value("Patient", {"name": args.patient}, ["customer"])

	deposit_balance = get_balance_on(party_type="Customer", party=customer, company=args.company)

	total_amount = 0
	for entry in summary_data:
		total_amount += entry["grand_total"]

	balance = (-1 * deposit_balance)

	current_balance = balance - total_amount

	currency = frappe.get_cached_value("Company", args.company, "default_currency")

	return [
		{
			"value": balance,
			"label": _("Total Deposited Amount"),
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

def get_last_row(args, data):
	total_beds = total_cons = total_labs = total_radiology = 0
	total_procedure = total_drug = total_therapy = total_grand = 0

	sorted_data = sorted(data, key=lambda x: x['date'])
	report_summary = get_report_summary(args, sorted_data)

	for n in range(0, len(sorted_data)):
		total_beds += sorted_data[n]['total_bed_charges']
		total_cons += sorted_data[n]['total_cons_charges']
		total_labs += sorted_data[n]['total_lab_amount']
		total_radiology += sorted_data[n]['total_radiology_amount']
		total_procedure += sorted_data[n]['total_procedure_amount']
		total_drug += sorted_data[n]['total_drug_amount']
		total_therapy += sorted_data[n]['total_therapy_amount']
		total_grand += sorted_data[n]['grand_total']
	
	sorted_data.append({
		'date': 'Total', 'service_unit': '', 'total_bed_charges': total_beds, 'total_cons_charges': total_cons,
		'total_lab_amount': total_labs, 'total_radiology_amount': total_radiology, 'total_procedure_amount': total_procedure,
		'total_drug_amount': total_drug, 'total_therapy_amount': total_therapy, 'grand_total': total_grand
	})
	return sorted_data, report_summary
