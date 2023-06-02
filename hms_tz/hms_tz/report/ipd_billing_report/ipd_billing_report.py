import frappe
from frappe import _, get_cached_value
from frappe.utils import flt, nowdate, getdate
from erpnext.accounts.utils import get_balance_on

<<<<<<< HEAD

def execute(filters=None):
    args = frappe._dict(filters or {})

    columns = get_columns()
    data, dashboard = get_data(args)

    return columns, data, None, None, dashboard


def get_columns():
    columns = [
        {"fieldname": "date", "fieldtype": "date", "label": _("Date"), "width": 120},
        {
            "fieldname": "service_unit",
            "fieldtype": "Data",
            "label": _("Service Unit"),
            "width": 120,
        },
        {
            "fieldname": "total_bed_charges",
            "fieldtype": "Currency",
            "label": _("Bed Charges"),
            "width": 120,
        },
        {
            "fieldname": "total_cons_charges",
            "fieldtype": "Currency",
            "label": _("Consultation Charges"),
            "width": 120,
        },
        {
            "fieldname": "total_lab_amount",
            "fieldtype": "Currency",
            "label": _("Lab Amount"),
            "width": 120,
        },
        {
            "fieldname": "total_radiology_amount",
            "fieldtype": "Currency",
            "label": _("Radiology Amount"),
            "width": 120,
        },
        {
            "fieldname": "total_procedure_amount",
            "fieldtype": "Currency",
            "label": _("Procedure Amount"),
            "width": 120,
        },
        {
            "fieldname": "total_drug_amount",
            "fieldtype": "Currency",
            "label": _("Medication Amount"),
            "width": 120,
        },
        {
            "fieldname": "total_therapy_amount",
            "fieldtype": "Currency",
            "label": _("Therapies Amount"),
            "width": 120,
        },
        {
            "fieldname": "grand_total",
            "fieldtype": "Currency",
            "label": _("Amount Used Per Day"),
            "width": 120,
        },
    ]

    return columns


def get_data(args):
    service_list = []
    date_list = []
    single_transaction_per_day = []
    mult_transaction_per_day = []
    transactions = get_transaction_data(args)
    for record in transactions:
        total_amount = (
            flt(record["bed_charges"])
            + flt(record["cons_charges"])
            + flt(record["lab_amount"])
            + flt(record["radiology_amount"])
            + flt(record["procedure_amount"])
            + flt(record["drug_amount"])
            + flt(record["therapy_amount"])
        )
=======
def execute(filters=None):
	args = frappe._dict(filters or {})
	if filters.get('summarized_view') == 1:
		columns = get_summarized_columns()

		data, dashboard = get_summarized_data(args)

		return columns, data, None, None, dashboard

	columns = get_columns()
	data = get_data(filters)
	return columns, data

def get_summarized_columns():
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

# itemized col report
def get_columns():
	columns = [
		{"fieldname": "date", "fieldtype": "date", "label": _("Date")},
		{"fieldname": "category", "fieldtype": "Data", "label": _("Category")},
		{"fieldname": "description", "fieldtype": "Data", "label": _("Description")},
		{"fieldname": "quantity", "fieldtype": "Data", "label": _("Quantity")},
		{"fieldname": "rate", "fieldtype": "Currency", "label": _("Rate")},
		{"fieldname": "amount", "fieldtype": "Currency", "label": _("Amount")},
	]
	return columns

def get_summarized_data(args):
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
>>>>>>> 1d8479c1 (feat: functionality to display item-wise and total-wise reports in the IPD report)

        date_d = record["date"].strftime("%Y-%m-%d")
        if date_d not in date_list:
            date_list.append(date_d)
            record.update({"total_amount": total_amount})
            single_transaction_per_day.append(record)
        else:
            record.update({"total_amount": total_amount})
            mult_transaction_per_day.append(record)

    for single_transaction in single_transaction_per_day:
        service_unit = ""
        mult_bed_charges = (
            mult_cons_charges
        ) = (
            mult_lab_amount
        ) = (
            mult_radiology_amount
        ) = (
            mult_procedure_amount
        ) = mult_drug_amount = mult_therapy_amount = mult_total_amount = 0

        single_transaction_date = single_transaction["date"].strftime("%Y-%m-%d")

        for mult_transaction in mult_transaction_per_day:
            mult_transaction_date = mult_transaction["date"].strftime("%Y-%m-%d")

            if single_transaction_date == mult_transaction_date:
                mult_bed_charges += flt(mult_transaction["bed_charges"])
                mult_cons_charges += flt(mult_transaction["cons_charges"])
                mult_lab_amount += flt(mult_transaction["lab_amount"])
                mult_radiology_amount += flt(mult_transaction["radiology_amount"])
                mult_procedure_amount += flt(mult_transaction["procedure_amount"])
                mult_drug_amount += flt(mult_transaction["drug_amount"])
                mult_therapy_amount += flt(mult_transaction["therapy_amount"])
                mult_total_amount += flt(mult_transaction["total_amount"])

                service_unit += mult_transaction["service_unit"]

        service_list.append(
            {
                "date": single_transaction_date,
                "service_unit": single_transaction["service_unit"] or service_unit,
                "total_bed_charges": flt(single_transaction["bed_charges"])
                + mult_bed_charges,
                "total_cons_charges": flt(single_transaction["cons_charges"])
                + mult_cons_charges,
                "total_lab_amount": flt(single_transaction["lab_amount"])
                + mult_lab_amount,
                "total_radiology_amount": flt(single_transaction["radiology_amount"])
                + mult_radiology_amount,
                "total_procedure_amount": flt(single_transaction["procedure_amount"])
                + mult_procedure_amount,
                "total_drug_amount": flt(single_transaction["drug_amount"])
                + mult_drug_amount,
                "total_therapy_amount": flt(single_transaction["therapy_amount"])
                + mult_therapy_amount,
                "grand_total": flt(single_transaction["total_amount"])
                + mult_total_amount,
            }
        )

    return get_last_row(args, service_list)


def get_transaction_data(args):
    services = frappe.db.sql(
        """
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
	""",
        args,
        as_dict=True,
    )

    return services


def get_report_summary(args, summary_data):
    customer = frappe.get_value("Patient", {"name": args.patient}, ["customer"])

    deposit_balance = get_balance_on(
        party_type="Customer", party=customer, company=args.company
    )

    total_amount = 0
    for entry in summary_data:
        total_amount += entry["grand_total"]

    balance = -1 * deposit_balance

    current_balance = balance - total_amount

    currency = frappe.get_cached_value("Company", args.company, "default_currency")

    return [
        {
            "value": balance,
            "label": _("Total Deposited Amount"),
            "datatype": "Currency",
            "currency": currency,
        },
        {
            "value": total_amount,
            "label": _("Total Amount Used"),
            "datatype": "Currency",
            "currency": currency,
        },
        {
            "value": current_balance,
            "label": _("Current Balance"),
            "datatype": "Currency",
            "currency": currency,
        },
    ]


def get_last_row(args, data):
    total_beds = total_cons = total_labs = total_radiology = 0
    total_procedure = total_drug = total_therapy = total_grand = 0

    sorted_data = sorted(data, key=lambda x: x["date"])
    report_summary = get_report_summary(args, sorted_data)

<<<<<<< HEAD
    for n in range(0, len(sorted_data)):
        total_beds += sorted_data[n]["total_bed_charges"]
        total_cons += sorted_data[n]["total_cons_charges"]
        total_labs += sorted_data[n]["total_lab_amount"]
        total_radiology += sorted_data[n]["total_radiology_amount"]
        total_procedure += sorted_data[n]["total_procedure_amount"]
        total_drug += sorted_data[n]["total_drug_amount"]
        total_therapy += sorted_data[n]["total_therapy_amount"]
        total_grand += sorted_data[n]["grand_total"]

    sorted_data.append(
        {
            "date": "Total",
            "service_unit": "",
            "total_bed_charges": total_beds,
            "total_cons_charges": total_cons,
            "total_lab_amount": total_labs,
            "total_radiology_amount": total_radiology,
            "total_procedure_amount": total_procedure,
            "total_drug_amount": total_drug,
            "total_therapy_amount": total_therapy,
            "grand_total": total_grand,
        }
    )
    return sorted_data, report_summary
=======
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

# itemized data report
def get_data(filters):
	data =  []
	details = frappe.get_all(
		"Patient Appointment",
		filters=[["patient", "=", filters.patient], ["name", "=", filters.appointment_no]],
		fields=[
			"docstatus", "status",
		]
	)

	if (details[0]["docstatus"] == 0 and details[0]["status"] != "Closed"):
		frappe.throw(frappe.bold("This Appointment is not Closed..!!"))
	
	else:
		if not filters.get('patient_type'):
			appointments_data = get_appointment_consultancy(filters)
			if appointments_data: data += appointments_data

			cash_lrpmt_data = get_cash_lrpmt_transaction(filters)
			if cash_lrpmt_data: data += cash_lrpmt_data

# 			insurance_lrpmt_data = get_insurance_lrpmt_transaction(filters)
# 			if insurance_lrpmt_data: data += insurance_lrpmt_data
			
			ipd_beds = get_ipd_occupancy_transactions(filters)
			if ipd_beds: data += ipd_beds

			ipd_cons = get_ipd_consultancy_transactions(filters)
			if ipd_cons: data += ipd_cons

			data = sorted(data, key=lambda d: d['date'])

			if not data:
				frappe.throw("No Record found for the filters Patient: {0}, Appointment: {1},\
					Patient Type: {2} From Date: {3} and To Date: {4} you specified..., \
					Please change your filters and try again..!!".format(
						frappe.bold(filters.patient),
						frappe.bold(filters.appointment_no),
						frappe.bold(filters.patient_type),
						frappe.bold(filters.from_date),
						frappe.bold(filters.to_date)
					)
				)

			total_amount = 0
			for n in range(0, len(data)):
				total_amount += data[n]["amount"]

			last_row = {"date": "Total", "category": "", "description": "", "quantity": "", "rate": "", "amount": total_amount, "patient": "",
				"patient_name": "", "appointment_type": "", "insurance_company": "", "coverage_plan_name": "", "authorization_number": "", 
				"coverage_plan_card_number": "", "admitted_date": "", "discharge_date": ""
			}

			print_person = frappe.get_value("User", frappe.session.user, "full_name")

			last_row["printed_by"] = print_person
			
			data.append(last_row)

			return data
		
		if filters.get('patient_type') == 'Out-Patient':
			appointments_data = get_appointment_consultancy(filters)
			if appointments_data: data += appointments_data

			cash_lrpmt_data = get_cash_lrpmt_transaction(filters)
			if cash_lrpmt_data: data += cash_lrpmt_data

# 			insurance_lrpmt_data = get_insurance_lrpmt_transaction(filters)
# 			if insurance_lrpmt_data: data += insurance_lrpmt_data

			data = sorted(data, key=lambda d: d['date'])

			if not data:
				frappe.throw("No Record found for the filters Patient: {0}, Appointment: {1},\
					Patient Type: {2} From Date: {3} and To Date: {4} you specified..., \
					Please change your filters and try again..!!".format(
						frappe.bold(filters.patient),
						frappe.bold(filters.appointment_no),
						frappe.bold(filters.patient_type),
						frappe.bold(filters.from_date),
						frappe.bold(filters.to_date)
					)
				)

			total_amount = 0
			for n in range(0, len(data)):
				total_amount += data[n]["amount"]

			last_row = {"date": "Total", "category": "", "description": "", "quantity": "", "rate": "", "amount": total_amount, "patient": "",
				"patient_name": "", "appointment_type": "", "insurance_company": "", "coverage_plan_name": "", "authorization_number": "", 
				"coverage_plan_card_number": "", "admitted_date": "", "discharge_date": ""
			}

			print_person = frappe.get_value("User", frappe.session.user, "full_name")

			last_row["printed_by"] = print_person
			
			data.append(last_row)

			return data
		
		if filters.get('patient_type') == 'In-Patient':
			cash_lrpmt_data = get_cash_lrpmt_transaction(filters)
			if cash_lrpmt_data: data += cash_lrpmt_data

# 			insurance_lrpmt_data = get_insurance_lrpmt_transaction(filters)
# 			if insurance_lrpmt_data: data += insurance_lrpmt_data
			
			ipd_beds = get_ipd_occupancy_transactions(filters)
			if ipd_beds: data += ipd_beds

			ipd_cons = get_ipd_consultancy_transactions(filters)
			if ipd_cons: data += ipd_cons

			data = sorted(data, key=lambda d: d['date'])
			if not data:
				frappe.throw("No Record found for the filters Patient: {0}, Appointment: {1},\
					Patient Type: {2} From Date: {3} and To Date: {4} you specified..., \
					Please change your filters and try again..!!".format(
						frappe.bold(filters.patient),
						frappe.bold(filters.appointment_no),
						frappe.bold(filters.patient_type),
						frappe.bold(filters.from_date),
						frappe.bold(filters.to_date)
					)
				)

			total_amount = 0
			for n in range(0, len(data)):
				total_amount += data[n]["amount"]

			last_row = {"date": "Total", "category": "", "description": "", "quantity": "", "rate": "", "amount": total_amount, "patient": "",
				"patient_name": "", "appointment_type": "", "insurance_company": "", "coverage_plan_name": "", "authorization_number": "", 
				"coverage_plan_card_number": "", "admitted_date": "", "discharge_date": ""
			}

			print_person = frappe.get_value("User", frappe.session.user, "full_name")

			last_row["printed_by"] = print_person
			
			data.append(last_row)
			# summary_view = get_report_summary_2(filters, total_amount)

			return data #, None, None, summary_view
		

def get_conditions(filters):
	if filters.get("patient"): 
		conditions = "and pa.patient = %(patient)s"

	if filters.get("appointment_no"):
		conditions += "and pa.name = %(appointment_no)s"

	if filters.get("from_date"): 
		conditions += " and pa.appointment_date >= %(from_date)s"

	if filters.get("to_date"): 
		conditions += " and pa.appointment_date <= %(to_date)s"

	return conditions

def get_enc_conditions(filters):
	if filters.get("patient"):
		conditions = " and pe.patient = %(patient)s"

	if filters.get("appointment_no"):
		conditions += " and pe.appointment = %(appointment_no)s"

	if filters.get("patient_type") == "Out-Patient":
		conditions += " and pe.inpatient_record is null "

	if filters.get("patient_type") == "In-Patient":
		conditions += " and pe.inpatient_record is not null "

	if filters.get("from_date"):
		conditions += " and pe.encounter_date >= %(from_date)s"

	if filters.get("to_date"):
		conditions += " and pe.encounter_date <= %(to_date)s"
	
	return conditions

def get_ipd_conditions(filters):
	if filters.get("patient"):
		conditions = " and ipd_rec.patient = %(patient)s"

	if filters.get("appointment_no"):
		conditions += " and ipd_rec.patient_appointment = %(appointment_no)s"

	if filters.get("from_date"):
		conditions += " and DATE(ipd_rec.admitted_datetime) >= %(from_date)s"

	if filters.get("to_date"):
		conditions += " and DATE(ipd_rec.admitted_datetime) <= %(to_date)s"
	
	return conditions

def get_appointment_consultancy(filters):
	conditions = get_conditions(filters)

	data = frappe.db.sql("""
		SELECT
			pa.appointment_date AS date,
			it.item_group AS category,
			pa.billing_item AS description,
			1 AS quantity,
			pa.paid_amount AS rate,
			pa.paid_amount AS amount,
			pa.patient AS patient,
			pa.patient_name AS patient_name,
			pa.appointment_type AS appointment_type,
			pa.insurance_company AS insurance_company,
			pa.coverage_plan_name AS coverage_plan_name,
			pa.authorization_number AS authorization_number,
			pa.coverage_plan_card_number AS coverage_plan_card_number,
			DATE(ipd_rec.admitted_datetime) as admitted_date,
			ipd_rec.discharge_date as discharge_date
		FROM `tabPatient Appointment` pa
			INNER JOIN `tabItem` it ON pa.billing_item = it.item_name
			LEFT JOIN `tabInpatient Record` ipd_rec ON pa.name = ipd_rec.patient_appointment
		WHERE pa.status = "Closed"
		AND pa.follow_up = 0 {conditions}
	""".format(conditions=conditions), filters, as_dict=1
	)
	return data

def get_ipd_occupancy_transactions(filters):
	ipd_conditions = get_ipd_conditions(filters)
	pe_conditions = get_enc_conditions(filters)

	data = frappe.db.sql("""
		SELECT
			DATE(ipd_occ.check_in) AS date,
			hsut.item_group AS category,
			ipd_occ.service_unit AS description,
			1 AS quantity,
			ipd_occ.amount AS rate,
			ipd_occ.amount AS amount,
			pa.patient AS patient,
			pa.patient_name AS patient_name,
			pa.appointment_type AS appointment_type,
			pa.insurance_company AS insurance_company,
			pa.coverage_plan_name AS coverage_plan_name,
			pa.authorization_number AS authorization_number,
			pa.coverage_plan_card_number AS coverage_plan_card_number,
			DATE(ipd_rec.admitted_datetime) as admitted_date,
			ipd_rec.discharge_date as discharge_date
		FROM `tabInpatient Occupancy` ipd_occ
			INNER JOIN `tabInpatient Record` ipd_rec ON ipd_occ.parent = ipd_rec.name
			INNER JOIN `tabHealthcare Service Unit` hsu ON ipd_occ.service_unit = hsu.name
			INNER JOIN `tabHealthcare Service Unit Type` hsut ON hsu.service_unit_type = hsut.name
			INNER JOIN `tabPatient Appointment` pa ON ipd_rec.patient_appointment = pa.name
		WHERE ipd_occ.is_confirmed = 1
		AND ipd_rec.admission_encounter IN (
			SELECT pe.name FROM `tabPatient Encounter` pe
			WHERE pe.docstatus = 1 {pe_conditions}
			ORDER BY pe.creation desc
		) {ipd_conditions}
	""".format(pe_conditions=pe_conditions, ipd_conditions=ipd_conditions), filters, as_dict=1
	)
	
	return data

def get_ipd_consultancy_transactions(filters):
	ipd_conditions = get_ipd_conditions(filters)
	pe_conditions = get_enc_conditions(filters)

	data = frappe.db.sql("""
		SELECT
			ipd_cons.date AS date,
			it.item_group AS category,
			ipd_cons.consultation_item AS description,
			1 AS quantity,
			ipd_cons.rate AS rate,
			ipd_cons.rate AS amount,
			pa.patient AS patient,
			pa.patient_name AS patient_name,
			pa.appointment_type AS appointment_type,
			pa.insurance_company AS insurance_company,
			pa.coverage_plan_name AS coverage_plan_name,
			pa.authorization_number AS authorization_number,
			pa.coverage_plan_card_number AS coverage_plan_card_number,
			DATE(ipd_rec.admitted_datetime) as admitted_date,
			ipd_rec.discharge_date as discharge_date
		FROM `tabInpatient Consultancy` ipd_cons
			INNER JOIN `tabInpatient Record` ipd_rec ON ipd_cons.parent = ipd_rec.name
			INNER JOIN `tabPatient Appointment` pa ON ipd_rec.patient_appointment = pa.name
			INNER JOIN `tabItem` it ON ipd_cons.consultation_item = it.item_name
		WHERE ipd_cons.is_confirmed = 1
		AND ipd_cons.encounter IN (
			SELECT pe.name FROM `tabPatient Encounter` pe
			WHERE pe.docstatus = 1 {pe_conditions}
			ORDER BY pe.creation desc
		) {ipd_conditions}
	""".format(pe_conditions=pe_conditions, ipd_conditions=ipd_conditions), filters, as_dict=1
	)
	return data

def get_cash_lrpmt_transaction(filters):
	conditions = get_enc_conditions(filters)

	data = frappe.db.sql("""
		SELECT
			DATE(lrpmt.creation) AS date,
			item_template.lab_test_group AS category,
			lrpmt.lab_test_name AS description,
			1 AS quantity,
			lrpmt.amount AS rate,
			lrpmt.amount AS amount,
			pa.patient AS patient,
			pa.patient_name AS patient_name,
			pa.appointment_type AS appointment_type,
			pa.insurance_company AS insurance_company,
			pa.coverage_plan_name AS coverage_plan_name,
			pa.authorization_number AS authorization_number,
			pa.coverage_plan_card_number AS coverage_plan_card_number,
			DATE(ipd_rec.admitted_datetime) as admitted_date,
			ipd_rec.discharge_date as discharge_date
		FROM `tabLab Prescription` lrpmt
			INNER JOIN `tabLab Test Template` item_template ON lrpmt.lab_test_code = item_template.name
			INNER JOIN `tabPatient Encounter` pe ON lrpmt.parent = pe.name
			INNER JOIN `tabPatient Appointment` pa ON pe.appointment = pa.name
			LEFT JOIN `tabInpatient Record` ipd_rec ON pa.name = ipd_rec.patient_appointment AND pe.name = ipd_rec.admission_encounter
		WHERE lrpmt.is_not_available_inhouse = 0
		AND lrpmt.is_cancelled = 0
		AND lrpmt.prescribe = 1
		AND lrpmt.parent IN (
			SELECT pe.name FROM `tabPatient Encounter` pe
			WHERE pe.mode_of_payment != ""
			AND  pe.docstatus = 1 {conditions}
			ORDER BY pe.creation desc
		)

		UNION ALL

		SELECT
			DATE(lrpmt.creation) AS date,
			item_template.item_group AS category,
			lrpmt.radiology_procedure_name AS description,
			1 AS quantity,
			lrpmt.amount AS rate,
			lrpmt.amount AS amount,
			pa.patient AS patient,
			pa.patient_name AS patient_name,
			pa.appointment_type AS appointment_type,
			pa.insurance_company AS insurance_company,
			pa.coverage_plan_name AS coverage_plan_name,
			pa.authorization_number AS authorization_number,
			pa.coverage_plan_card_number AS coverage_plan_card_number,
			DATE(ipd_rec.admitted_datetime) as admitted_date,
			ipd_rec.discharge_date as discharge_date
		FROM `tabRadiology Procedure Prescription` lrpmt
			INNER JOIN `tabRadiology Examination Template` item_template ON lrpmt.radiology_examination_template = item_template.name
			INNER JOIN `tabPatient Encounter` pe ON lrpmt.parent = pe.name
			INNER JOIN `tabPatient Appointment` pa ON pe.appointment = pa.name
			LEFT JOIN `tabInpatient Record` ipd_rec ON pa.name = ipd_rec.patient_appointment AND pe.name = ipd_rec.admission_encounter
		WHERE lrpmt.is_not_available_inhouse = 0
		AND lrpmt.is_cancelled = 0
		AND lrpmt.prescribe = 1
		AND lrpmt.parent IN (
			SELECT pe.name FROM `tabPatient Encounter` pe
			WHERE pe.mode_of_payment != ""
			AND  pe.docstatus = 1 {conditions}
			ORDER BY pe.creation desc
		)

		UNION ALL

		SELECT
			DATE(lrpmt.creation) AS date,
			item_template.item_group AS category,
			lrpmt.procedure_name AS description,
			1 AS quantity, lrpmt.amount AS rate,
			lrpmt.amount AS amount,
			pa.patient AS patient,
			pa.patient_name AS patient_name,
			pa.appointment_type AS appointment_type,
			pa.insurance_company AS insurance_company,
			pa.coverage_plan_name AS coverage_plan_name,
			pa.authorization_number AS authorization_number,
			pa.coverage_plan_card_number AS coverage_plan_card_number,
			DATE(ipd_rec.admitted_datetime) as admitted_date,
			ipd_rec.discharge_date as discharge_date
		FROM `tabProcedure Prescription` lrpmt
			INNER JOIN `tabClinical Procedure Template` item_template ON lrpmt.procedure = item_template.name
			INNER JOIN `tabPatient Encounter` pe ON lrpmt.parent = pe.name
			INNER JOIN `tabPatient Appointment` pa ON pe.appointment = pa.name
			LEFT JOIN `tabInpatient Record` ipd_rec ON pa.name = ipd_rec.patient_appointment AND pe.name = ipd_rec.admission_encounter
		WHERE lrpmt.is_not_available_inhouse = 0
		AND lrpmt.is_cancelled = 0
		AND lrpmt.prescribe = 1
		AND lrpmt.parent IN (
			SELECT pe.name FROM `tabPatient Encounter` pe
			WHERE pe.mode_of_payment != ""
			AND  pe.docstatus = 1 {conditions}
			ORDER BY pe.creation desc
		)

		UNION ALL

		SELECT
			DATE(lrpmt.creation) AS date,
			item_template.item_group AS category,
			lrpmt.drug_name AS description,
			(lrpmt.quantity - lrpmt.quantity_returned) AS quantity,
			lrpmt.amount AS rate,
			((lrpmt.quantity - lrpmt.quantity_returned) * lrpmt.amount) AS amount,
			pa.patient AS patient,
			pa.patient_name AS patient_name,
			pa.appointment_type AS appointment_type,
			pa.insurance_company AS insurance_company,
			pa.coverage_plan_name AS coverage_plan_name,
			pa.authorization_number AS authorization_number,
			pa.coverage_plan_card_number AS coverage_plan_card_number,
			DATE(ipd_rec.admitted_datetime) as admitted_date,
			ipd_rec.discharge_date as discharge_date
		FROM `tabDrug Prescription` lrpmt
			INNER JOIN `tabMedication` item_template ON lrpmt.drug_code = item_template.name
			INNER JOIN `tabPatient Encounter` pe ON lrpmt.parent = pe.name
			INNER JOIN `tabPatient Appointment` pa ON pe.appointment = pa.name
			LEFT JOIN `tabInpatient Record` ipd_rec ON pa.name = ipd_rec.patient_appointment AND pe.name = ipd_rec.admission_encounter
		WHERE lrpmt.is_not_available_inhouse = 0
		AND lrpmt.is_cancelled = 0
		AND lrpmt.prescribe = 1
		AND lrpmt.docstatus = 1
		AND lrpmt.parent IN (
			SELECT pe.name FROM `tabPatient Encounter` pe
			WHERE pe.mode_of_payment != ""
			AND  pe.docstatus = 1 {conditions}
			ORDER BY pe.creation desc
		)

		UNION ALL

		SELECT
			DATE(lrpmt.creation) AS date,
			item_template.item_group AS category,
			lrpmt.therapy_type AS description,
			1 AS quantity,
			lrpmt.amount AS rate,
			lrpmt.amount AS amount,
			pa.patient AS patient,
			pa.patient_name AS patient_name,
			pa.appointment_type AS appointment_type,
			pa.insurance_company AS insurance_company,
			pa.coverage_plan_name AS coverage_plan_name,
			pa.authorization_number AS authorization_number,
			pa.coverage_plan_card_number AS coverage_plan_card_number,
			DATE(ipd_rec.admitted_datetime) as admitted_date,
			ipd_rec.discharge_date as discharge_date
		FROM `tabTherapy Plan Detail` lrpmt
			INNER JOIN `tabTherapy Type` item_template ON lrpmt.therapy_type = item_template.name
			INNER JOIN `tabPatient Encounter` pe ON lrpmt.parent = pe.name
			INNER JOIN `tabPatient Appointment` pa ON pe.appointment = pa.name
			LEFT JOIN `tabInpatient Record` ipd_rec ON pa.name = ipd_rec.patient_appointment AND pe.name = ipd_rec.admission_encounter
		WHERE lrpmt.is_not_available_inhouse = 0
		AND lrpmt.is_cancelled = 0
		AND lrpmt.prescribe = 1
		AND lrpmt.parent IN (
			SELECT pe.name FROM `tabPatient Encounter` pe
			WHERE pe.mode_of_payment != ""
			AND  pe.docstatus = 1 {conditions}
			ORDER BY pe.creation desc
		)
	""".format(conditions=conditions), filters, as_dict=1
	)

	return data

def get_insurance_lrpmt_transaction(filters):
	conditions = get_enc_conditions(filters)
	
	data = frappe.db.sql("""
		SELECT
			DATE(lrpmt.creation) AS date,
			item_template.lab_test_group AS category,
			lrpmt.lab_test_name AS description,
			1 AS quantity, lrpmt.amount AS rate,
			lrpmt.amount AS amount,
			pa.patient AS patient,
			pa.patient_name AS patient_name,
			pa.appointment_type AS appointment_type,
			pa.insurance_company AS insurance_company,
			pa.coverage_plan_name AS coverage_plan_name,
			pa.authorization_number AS authorization_number,
			pa.coverage_plan_card_number AS coverage_plan_card_number,
			DATE(ipd_rec.admitted_datetime) as admitted_date,
			ipd_rec.discharge_date as discharge_date
		FROM `tabLab Prescription` lrpmt
			INNER JOIN `tabLab Test Template` item_template ON lrpmt.lab_test_code = item_template.name
			INNER JOIN `tabPatient Encounter` pe ON lrpmt.parent = pe.name
			INNER JOIN `tabPatient Appointment` pa ON pe.appointment = pa.name
			LEFT JOIN `tabInpatient Record` ipd_rec ON pa.name = ipd_rec.patient_appointment AND pe.name = ipd_rec.admission_encounter
		WHERE lrpmt.prescribe = 0
		AND lrpmt.is_cancelled = 0
		AND lrpmt.is_not_available_inhouse = 0
		AND lrpmt.parent IN (
			SELECT pe.name FROM `tabPatient Encounter` pe
			WHERE pe.insurance_coverage_plan != ""
			AND pe.docstatus = 1 {conditions}
			ORDER BY pe.creation desc
		)

		UNION ALL

		SELECT
			DATE(lrpmt.creation) AS date,
			item_template.item_group AS category,
			lrpmt.radiology_procedure_name AS description,
			1 AS quantity,
			lrpmt.amount AS rate,
			lrpmt.amount AS amount,
			pa.patient AS patient,
			pa.patient_name AS patient_name,
			pa.appointment_type AS appointment_type,
			pa.insurance_company AS insurance_company,
			pa.coverage_plan_name AS coverage_plan_name,
			pa.authorization_number AS authorization_number,
			pa.coverage_plan_card_number AS coverage_plan_card_number,
			DATE(ipd_rec.admitted_datetime) as admitted_date,
			ipd_rec.discharge_date as discharge_date
		FROM `tabRadiology Procedure Prescription` lrpmt
			INNER JOIN `tabRadiology Examination Template` item_template ON lrpmt.radiology_examination_template = item_template.name
			INNER JOIN `tabPatient Encounter` pe ON lrpmt.parent = pe.name
			INNER JOIN `tabPatient Appointment` pa ON pe.appointment = pa.name
			LEFT JOIN `tabInpatient Record` ipd_rec ON pa.name = ipd_rec.patient_appointment AND pe.name = ipd_rec.admission_encounter
		WHERE lrpmt.prescribe = 0
		AND lrpmt.is_cancelled = 0
		AND lrpmt.is_not_available_inhouse = 0
		AND lrpmt.parent IN (
			SELECT pe.name FROM `tabPatient Encounter` pe
			WHERE pe.insurance_coverage_plan != ""
			AND pe.docstatus = 1 {conditions}
			ORDER BY pe.creation desc
		)

		UNION ALL

		SELECT
			DATE(lrpmt.creation) AS date,
			item_template.item_group AS category,
			lrpmt.procedure_name AS description,
			1 AS quantity,
			lrpmt.amount AS rate,
			lrpmt.amount AS amount, pa.patient AS patient,
			pa.patient_name AS patient_name,
			pa.appointment_type AS appointment_type,
			pa.insurance_company AS insurance_company,
			pa.coverage_plan_name AS coverage_plan_name,
			pa.authorization_number AS authorization_number,
			pa.coverage_plan_card_number AS coverage_plan_card_number,
			DATE(ipd_rec.admitted_datetime) as admitted_date,
			ipd_rec.discharge_date as discharge_date
		FROM `tabProcedure Prescription` lrpmt
			INNER JOIN `tabClinical Procedure Template` item_template ON lrpmt.procedure = item_template.name
			INNER JOIN `tabPatient Encounter` pe ON lrpmt.parent = pe.name
			INNER JOIN `tabPatient Appointment` pa ON pe.appointment = pa.name
			LEFT JOIN `tabInpatient Record` ipd_rec ON pa.name = ipd_rec.patient_appointment AND pe.name = ipd_rec.admission_encounter
		WHERE lrpmt.prescribe = 0
		AND lrpmt.is_cancelled = 0
		AND lrpmt.is_not_available_inhouse = 0
		AND lrpmt.parent IN (
			SELECT pe.name FROM `tabPatient Encounter` pe
			WHERE pe.insurance_coverage_plan != ""
			AND pe.docstatus = 1 {conditions}
			ORDER BY pe.creation desc
		)

		UNION ALL

		SELECT
			DATE(lrpmt.creation) AS date,
			item_template.item_group AS category,
			lrpmt.drug_name AS description,
			(lrpmt.quantity - lrpmt.quantity_returned) AS quantity,
			lrpmt.amount AS rate,
			((lrpmt.quantity - lrpmt.quantity_returned) * lrpmt.amount) AS amount,
			pa.patient AS patient,
			pa.patient_name AS patient_name,
			pa.appointment_type AS appointment_type,
			pa.insurance_company AS insurance_company,
			pa.coverage_plan_name AS coverage_plan_name,
			pa.authorization_number AS authorization_number,
			pa.coverage_plan_card_number AS coverage_plan_card_number,
			DATE(ipd_rec.admitted_datetime) as admitted_date,
			ipd_rec.discharge_date as discharge_date
		FROM `tabDrug Prescription` lrpmt
			INNER JOIN `tabMedication` item_template ON lrpmt.drug_code = item_template.name
			INNER JOIN `tabPatient Encounter` pe ON lrpmt.parent = pe.name
			INNER JOIN `tabPatient Appointment` pa ON pe.appointment = pa.name
			LEFT JOIN `tabInpatient Record` ipd_rec ON pa.name = ipd_rec.patient_appointment AND pe.name = ipd_rec.admission_encounter
		WHERE lrpmt.prescribe = 0
		AND lrpmt.is_cancelled = 0
		AND lrpmt.is_not_available_inhouse = 0
		AND lrpmt.parent IN (
			SELECT pe.name FROM `tabPatient Encounter` pe
			WHERE pe.insurance_coverage_plan != ""
			AND pe.docstatus = 1 {conditions}
			ORDER BY pe.creation desc
		)

		UNION ALL

		SELECT
			DATE(lrpmt.creation) AS date,
			item_template.item_group AS category,
			lrpmt.therapy_type AS description,
			1 AS quantity,
			lrpmt.amount AS rate,
			lrpmt.amount AS amount,
			pa.patient AS patient,
			pa.patient_name AS patient_name,
			pa.appointment_type AS appointment_type,
			pa.insurance_company AS insurance_company,
			pa.coverage_plan_name AS coverage_plan_name,
			pa.authorization_number AS authorization_number,
			pa.coverage_plan_card_number AS coverage_plan_card_number,
			DATE(ipd_rec.admitted_datetime) as admitted_date,
			ipd_rec.discharge_date as discharge_date
		FROM `tabTherapy Plan Detail` lrpmt
			INNER JOIN `tabTherapy Type` item_template ON lrpmt.therapy_type = item_template.name
			INNER JOIN `tabPatient Encounter` pe ON lrpmt.parent = pe.name
			INNER JOIN `tabPatient Appointment` pa ON pe.appointment = pa.name
			LEFT JOIN `tabInpatient Record` ipd_rec ON pa.name = ipd_rec.patient_appointment AND pe.name = ipd_rec.admission_encounter
		WHERE lrpmt.prescribe = 0
		AND lrpmt.is_cancelled = 0
		AND lrpmt.is_not_available_inhouse = 0
		AND lrpmt.parent IN (
			SELECT pe.name FROM `tabPatient Encounter` pe
			WHERE pe.insurance_coverage_plan != ""
			AND pe.docstatus = 1 {conditions}
			ORDER BY pe.creation desc
		)
	""".format(conditions=conditions), filters, as_dict=1
	)

	return data

def get_report_summary_2(filters, total_amount):
	customer = frappe.get_value('Patient', filters.get('patient'), 'customer')
	company = frappe.get_value('Patient Appointment', filters.get('appointment_no'), 'company')

	deposit_balance = -1 * get_balance_on(party_type='Customer', party=customer, company=company)

	current_balance = flt(flt(deposit_balance) - flt(total_amount))
	
	currency = frappe.get_cached_value("Company", company, "default_currency")

	return [
		{
			"value": deposit_balance,
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
>>>>>>> 1d8479c1 (feat: functionality to display item-wise and total-wise reports in the IPD report)
