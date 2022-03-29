# Copyright (c) 2022, Aakvatech and contributors
# For license information, please see license.txt

import frappe
from frappe import msgprint, _


def execute(filters=None):
	columns = get_columns(filters)

	data = []

	app_data = get_insurance_appointment_transactions(filters)
	lab_data = get_insurance_lab_transactions(filters)
	rad_data = get_insurance_radiology_transactions(filters)
	proc_data = get_insurance_procedure_transactions(filters)
	drug_data = get_insurance_drug_transactions(filters)
	ther_data = get_insurance_therapy_transactions(filters)
	inptient_occupancy_data = get_insurance_transactions_for_inpatient_occupancy(filters)
	inpatient_consultancy_data = get_insurance_transactions_for_inpatient_consultancy(filters)
	nhif_appointment_data = get_nhif_appointment_revenue(filters)
	nhif_lrpmt_data = get_nhif_LRPMT_revenue(filters)
	nhif_inpatient_data = get_nhif_inpatient_revenue(filters)
    # cash_transaction_data = get_cash_transactions(filters)

	if app_data:
		data += app_data
	if lab_data:
		data += lab_data
	if rad_data:
		data += rad_data
	if proc_data:
		data += proc_data
	if drug_data:
		data += drug_data
	if ther_data:
		data += ther_data
	if inptient_occupancy_data:
		data += inptient_occupancy_data
	if inpatient_consultancy_data:
		data += inpatient_consultancy_data
	if nhif_appointment_data:
		data += nhif_appointment_data
	if nhif_lrpmt_data:
		data += nhif_lrpmt_data
	if nhif_inpatient_data:
		data += nhif_inpatient_data
    # if cash_transaction_data:
    #     data += cash_transaction_data

	return columns, data


def get_columns(filters):
    columns = [
        {"fieldname": "year", "fieldtype": "Int", "label": _("Year")},
        {"fieldname": "month", "fieldtype": "Data", "label": _("Month")},
        {"fieldname": "healthcare_practitioner", "fieldtype": "Data", "label": _("Practitioner")},
        {"fieldname": "healthcare_practitioner_type", "fieldtype": "Data", "label": _("Practitioner Type")},
        {"fieldname": "practitioner_hsu", "fieldtype": "Data", "label": _("Practitioner HSU")},
        {"fieldname": "department_hsu", "fieldtype": "Data", "label": _("Department HSU")},
        {"fieldname": "amount", "fieldtype": "Currency", "label": _("Amount")},
        {"fieldname": "line_of_revenue", "fieldtype": "Data", "label": _("Line of Revenue")},
        {"fieldname": "payment_mode", "fieldtype": "Data", "label": _("Payment Mode")},
        {"fieldname": "speciality", "fieldtype": "Data", "label": _("Speciality")},
		{"fieldname": "main_department", "fieldtype": "Data", "label": _("Main Department")},
        {"fieldname": "status", "fieldtype": "Data", "label": _("Status")},
    ]
    return columns


# Patient Consultanct Fees From Insurances
def get_insurance_appointment_transactions(filters):
    conditions = ""
    if filters.get("from_date"):
        conditions += "AND date(pa.appointment_date) >= %(from_date)s"
    if filters.get("to_date"):
        conditions += "AND date(pa.appointment_date) <= %(to_date)s"
    if filters.get("company"):
        conditions += "AND pa.company = %(company)s"
    
    data = frappe.db.sql("""
        SELECT 
			YEAR(pa.appointment_date) AS year,
			MONTHNAME(pa.appointment_date) AS month,
			pa.practitioner AS healthcare_practitioner,
            hp.healthcare_practitioner_type AS healthcare_practitioner_type,
			pa.service_unit AS practitioner_hsu,
			pa.service_unit AS department_hsu,
			SUM(pa.paid_amount) AS amount,
			"Consultation" AS line_of_revenue,
			pa.coverage_plan_name AS payment_mode, 
			hp.department AS speciality,
			md.main_department AS main_department,
			"Submitted" AS status
		FROM `tabPatient Appointment` pa 
			INNER JOIN `tabHealthcare Practitioner` hp ON pa.practitioner = hp.name
            INNER JOIN `tabHealthcare Insurance Coverage Plan` hicp ON pa.coverage_plan_name = hicp.coverage_plan_name
			LEFT JOIN `tabMedical Department` md ON hp.department = md.name
		WHERE pa.insurance_company != ""
        AND hicp.hms_tz_has_nhif_coverage = 0 
        AND  pa.status = 'Closed' 
		AND pa.follow_up = 0 {conditions}
		GROUP BY 
			YEAR(pa.appointment_date), 
			MONTHNAME(pa.appointment_date), 
			pa.practitioner,
            hp.healthcare_practitioner_type,
			pa.service_unit, 
			pa.coverage_plan_name,
			hp.department,
			md.main_department
	""".format(conditions=conditions), filters, as_dict=1,
    )
    return data


# Lab Revenue From Insurances
def get_insurance_lab_transactions(filters):
    conditions = get_conditions(filters)

    data = frappe.db.sql("""
        SELECT 
			YEAR(pe.encounter_date) AS year, 
			MONTHNAME(pe.encounter_date) AS month, 
			pe.practitioner AS healthcare_practitioner,
            hp.healthcare_practitioner_type AS healthcare_practitioner_type,
			pe.healthcare_service_unit AS practitioner_hsu, 
			hsp.department_hsu AS department_hsu, 
			SUM(hsp.amount) AS amount, 
			"Lab" AS line_of_revenue, 
			pe.insurance_coverage_plan AS payment_mode, 
			hp.department AS speciality,
			md.main_department AS main_department,
			IF(MAX(hs_doc.docstatus) = 1, "Submitted", "Draft") AS status
		FROM `tabLab Prescription` hsp
			INNER JOIN `tabPatient Encounter` pe ON hsp.parent = pe.name
            INNER JOIN `tabHealthcare Insurance Coverage Plan` hicp ON pe.insurance_coverage_plan = hicp.coverage_plan_name
			INNER JOIN `tabHealthcare Practitioner` hp ON pe.practitioner = hp.name
			LEFT JOIN `tabMedical Department` md ON hp.department = md.name
			LEFT OUTER JOIN `tabLab Test` hs_doc ON hsp.lab_test = hs_doc.name 
                AND hs_doc.docstatus IN (0, 1)
		WHERE pe.insurance_company != ""
        AND hicp.hms_tz_has_nhif_coverage = 0
		AND hsp.docstatus = 1 
		AND hsp.prescribe = 0
        AND hsp.is_not_available_inhouse = 0 
		AND hsp.is_cancelled = 0 {conditions}
		GROUP BY 
			year(pe.encounter_date), 
			monthname(pe.encounter_date), 
			pe.practitioner,
            hp.healthcare_practitioner_type,
			pe.healthcare_service_unit, 
			hsp.department_hsu, 
			pe.insurance_coverage_plan,
			hp.department,
			md.main_department,
			hs_doc.docstatus
	""".format(conditions=conditions), filters, as_dict=1,
    )
    return data


# Radiology Revenue From Insurances
def get_insurance_radiology_transactions(filters):
    conditions = get_conditions(filters)

    data = frappe.db.sql("""
        SELECT 
			YEAR(pe.encounter_date) AS year, 
			MONTHNAME(pe.encounter_date) AS month, 
			pe.practitioner AS healthcare_practitioner,
            hp.healthcare_practitioner_type AS healthcare_practitioner_type,
			pe.healthcare_service_unit AS practitioner_hsu, 
			hsp.department_hsu AS department_hsu, 
			SUM(hsp.amount) AS amount, 
			"Radiology" AS line_of_revenue, 
			pe.insurance_coverage_plan AS payment_mode, 
			hp.department AS speciality,
			md.main_department AS main_department,
			IF(MAX(hs_doc.docstatus) = 1, "Submitted", "Draft") AS status
		FROM `tabRadiology Procedure Prescription` hsp
			INNER JOIN `tabPatient Encounter` pe ON hsp.parent = pe.name
            INNER JOIN `tabHealthcare Insurance Coverage Plan` hicp ON pe.insurance_coverage_plan = hicp.coverage_plan_name
			INNER JOIN `tabHealthcare Practitioner` hp ON pe.practitioner = hp.name
			LEFT JOIN `tabMedical Department` md ON hp.department = md.name
			LEFT OUTER JOIN `tabRadiology Examination` hs_doc ON hsp.radiology_examination = hs_doc.name
                AND hs_doc.docstatus IN (0, 1)
		WHERE pe.insurance_company != ""
        AND hicp.hms_tz_has_nhif_coverage = 0
		AND hsp.docstatus = 1 
		AND hsp.prescribe = 0
        AND hsp.is_not_available_inhouse = 0 
		AND hsp.is_cancelled = 0 {conditions}
		GROUP BY 
			year(pe.encounter_date), 
			month(pe.encounter_date), 
			pe.practitioner,
            hp.healthcare_practitioner_type,
			pe.healthcare_service_unit, 
			hsp.department_hsu, 
			pe.insurance_coverage_plan,
			hp.department,
			md.main_department,
			hs_doc.docstatus
	""".format(conditions=conditions), filters, as_dict=1,
    )
    return data


# Clinical Procedure Revenue From Insurances
def get_insurance_procedure_transactions(filters):
    conditions = get_conditions(filters)

    return frappe.db.sql(
        """
		SELECT 
			YEAR(pe.encounter_date) AS year, 
			MONTHNAME(pe.encounter_date) AS month, 
			pe.practitioner AS healthcare_practitioner,
            hp.healthcare_practitioner_type AS healthcare_practitioner_type,
			pe.healthcare_service_unit AS practitioner_hsu, 
			hsp.department_hsu AS department_hsu, 
			SUM(hsp.amount) AS amount, 
			"Clinical Procedure" AS line_of_revenue, 
			pe.insurance_coverage_plan AS payment_mode, 
			hp.department AS speciality,
			md.main_department AS main_department,
			IF(MAX(hs_doc.docstatus) = 1, "Submitted", "Draft") AS status
		FROM `tabProcedure Prescription` hsp
			INNER JOIN `tabPatient Encounter` pe ON pe.name = hsp.parent
            INNER JOIN `tabHealthcare Insurance Coverage Plan` hicp ON pe.insurance_coverage_plan = hicp.coverage_plan_name
			INNER JOIN `tabHealthcare Practitioner` hp ON pe.practitioner = hp.name
			LEFT JOIN `tabMedical Department` md ON hp.department = md.name
			LEFT OUTER JOIN `tabClinical Procedure` hs_doc ON hsp.clinical_procedure = hs_doc.name
                AND hs_doc.docstatus IN (0, 1)
		WHERE pe.insurance_company != ""
        AND hicp.hms_tz_has_nhif_coverage = 0
		AND hsp.docstatus = 1 
		AND hsp.prescribe = 0
        AND hsp.is_not_available_inhouse = 0 
		AND hsp.is_cancelled = 0 {conditions}
		GROUP BY 
			YEAR(pe.encounter_date), 
			MONTH(pe.encounter_date), 
			pe.practitioner,
            hp.healthcare_practitioner_type,
			pe.healthcare_service_unit, 
			hsp.department_hsu, 
			pe.insurance_coverage_plan,
			hp.department,
			md.main_department,
			hs_doc.docstatus
	""".format(conditions=conditions),  filters, as_dict=1,
    )


# Drug Prescription From Insurances
def get_insurance_drug_transactions(filters):
    conditions = get_conditions(filters)

    data = frappe.db.sql(
        """
		SELECT 
			YEAR(pe.encounter_date) AS year,
			MONTHNAME(pe.encounter_date) AS month,
			pe.practitioner AS healthcare_practitioner,
            hp.healthcare_practitioner_type AS healthcare_practitioner_type,
			pe.healthcare_service_unit AS practitioner_hsu,
			hsp.healthcare_service_unit  AS department_hsu, 
			SUM(hsp.amount * (hsp.quantity - hsp.quantity_returned)) AS amount, 
			"Medication" AS line_of_revenue,
			pe.insurance_coverage_plan AS payment_mode, 
			hp.department AS speciality,
			md.main_department AS main_department,
			IF(MAX(hs_doc.docstatus) = 1, "Submitted", "Draft") AS status
		FROM `tabDrug Prescription` hsp
			INNER JOIN `tabPatient Encounter` pe ON pe.name = hsp.parent
            INNER JOIN `tabHealthcare Insurance Coverage Plan` hicp ON pe.insurance_coverage_plan = hicp.coverage_plan_name
			INNER JOIN `tabHealthcare Practitioner` hp ON pe.practitioner = hp.name
			LEFT JOIN `tabMedical Department` md ON hp.department = md.name
            LEFT OUTER JOIN `tabDelivery Note Item` hs_doc ON hsp.name = hs_doc.reference_name 
                AND hs_doc.reference_doctype = "Drug Prescription" AND hs_doc.docstatus IN (0, 1)
            LEFT OUTER JOIN `tabDelivery Note` dn ON hs_doc.parent = dn.name AND dn.docstatus IN (0, 1)
                AND dn.is_return = 0 
		WHERE pe.insurance_company != ""
        AND hicp.hms_tz_has_nhif_coverage = 0
		AND hsp.docstatus = 1 
		AND hsp.prescribe = 0
        AND hsp.is_not_available_inhouse = 0 
		AND hsp.is_cancelled = 0 {conditions}
		GROUP BY 
			year(pe.encounter_date),
			month(pe.encounter_date),
			pe.practitioner,
            hp.healthcare_practitioner_type,
			pe.healthcare_service_unit, 
			hsp.healthcare_service_unit,
			pe.insurance_coverage_plan,
			hp.department,
			md.main_department,
			hs_doc.docstatus
	""".format(conditions=conditions), filters, as_dict=1,
    )
    return data


# Therapy Revenue From Insurances
def get_insurance_therapy_transactions(filters):
    conditions = get_conditions(filters)

    data = frappe.db.sql(
        """
		SELECT 
			YEAR(pe.encounter_date) AS year,
			MONTHNAME(pe.encounter_date) AS month,
			pe.practitioner AS healthcare_practitioner,
            hp.healthcare_practitioner_type AS healthcare_practitioner_type,
			pe.healthcare_service_unit AS practitioner_hsu,
			hsp.department_hsu AS department_hsu,
			SUM(hsp.amount) AS amount,
			"Therapy" AS line_of_revenue,
			pe.insurance_coverage_plan AS payment_mode, 
			hp.department AS speciality,
			md.main_department AS main_department,
			IF(1 = 1, "Submitted", "Draft") AS status
		FROM `tabTherapy Plan Detail` hsp
			INNER JOIN `tabPatient Encounter` pe ON pe.name = hsp.parent
            INNER JOIN `tabHealthcare Insurance Coverage Plan` hicp ON pe.insurance_coverage_plan = hicp.coverage_plan_name
			INNER JOIN `tabHealthcare Practitioner` hp ON pe.practitioner = hp.name
			LEFT JOIN `tabMedical Department` md ON hp.department = md.name
		WHERE pe.insurance_company != ""
        AND hicp.hms_tz_has_nhif_coverage = 0
		AND hsp.docstatus = 1 
		AND hsp.prescribe = 0
        AND hsp.is_not_available_inhouse = 0 
		AND hsp.is_cancelled = 0 {conditions}
		GROUP BY 
			YEAR(pe.encounter_date),
			MONTH(pe.encounter_date),
			pe.practitioner,
            hp.healthcare_practitioner_type,
			pe.healthcare_service_unit,
			hsp.department_hsu,
			pe.insurance_coverage_plan, 
			hp.department,
			md.main_department, 1
	""".format(conditions=conditions), filters, as_dict=1,
    )
    return data


def get_conditions(filters):
    conditions = ""

    if filters.get("from_date"):
        conditions += "AND pe.encounter_date >= %(from_date)s"
    if filters.get("to_date"):
        conditions += "AND pe.encounter_date <= %(to_date)s"
    if filters.get("company"):
        conditions += "AND pe.company = %(company)s and pe.docstatus = 1"

    return conditions


# IPD Bed Charges From Insurances
def get_insurance_transactions_for_inpatient_occupancy(filters):
    # enc_conditions = get_conditions(filters)
    # ipd_conditions = get_ipd_conditions(filters)

    data = frappe.db.sql(
        """
		SELECT 
			YEAR(DATE(ipd_occ.check_in)) AS year,
			MONTHNAME(DATE(ipd_occ.check_in)) AS month,
			null AS healthcare_practitioner,
			null AS healthcare_practitioner_type,
			null AS practitioner_hsu,
			ipd_occ.service_unit AS department_hsu,
			SUM(ipd_occ.amount) as amount, 
			"IPD" AS line_of_revenue,
			pa.coverage_plan_name AS payment_mode,
			hsut.item_group AS speciality,
			null AS main_department,
			"Confirmed" AS status
		FROM `tabInpatient Occupancy` ipd_occ
			INNER JOIN `tabInpatient Record` ipd_rec ON ipd_occ.parent = ipd_rec.name
            INNER JOIN `tabHealthcare Insurance Coverage Plan` hicp ON ipd_rec.insurance_coverage_plan = hicp.coverage_plan_name
			INNER JOIN `tabHealthcare Service Unit` hsu ON ipd_occ.service_unit = hsu.name
			INNER JOIN `tabHealthcare Service Unit Type` hsut ON hsu.service_unit_type = hsut.name
			INNER JOIN `tabPatient Appointment` pa ON ipd_rec.patient_appointment = pa.name
		WHERE ipd_rec.company = %(company)s
		AND ipd_rec.insurance_subscription != ""
        AND hicp.hms_tz_has_nhif_coverage = 0
		AND ipd_occ.check_in BETWEEN %(from_date)s AND %(to_date)s
		AND ipd_occ.is_confirmed = 1
		GROUP BY 
			YEAR(DATE(ipd_rec.admitted_datetime)), 
			MONTHNAME(DATE(ipd_rec.admitted_datetime)), 
			ipd_occ.service_unit,
			hsut.item_group, 
			pa.coverage_plan_name
	""", filters, as_dict=1)
    return data


# IPD Consultancy From Insurances
def get_insurance_transactions_for_inpatient_consultancy(filters):
    # enc_conditions = get_conditions(filters)
    # ipd_conditions = get_ipd_conditions(filters)

    data = frappe.db.sql(
        """
		SELECT 
			YEAR(DATE(ipd_cons.date)) AS year, 
			MONTHNAME(DATE(ipd_cons.date)) AS month,
			pe.practitioner AS healthcare_practitioner,
            hp.healthcare_practitioner_type AS healthcare_practitioner_type,
			pe.healthcare_service_unit AS practitioner_hsu, 
			null AS department_hsu,
			SUM(ipd_cons.rate) AS amount, 
			"IPD" AS line_of_revenue,
			pa.coverage_plan_name AS payment_mode,
			it.item_group AS speciality, 
			null AS main_department, "Confirmed" AS status
		FROM `tabInpatient Consultancy` ipd_cons
			INNER JOIN `tabInpatient Record` ipd_rec ON ipd_cons.parent = ipd_rec.name
            INNER JOIN `tabHealthcare Insurance Coverage Plan` hicp ON ipd_rec.insurance_coverage_plan = hicp.coverage_plan_name
			INNER JOIN `tabPatient Appointment` pa ON ipd_rec.patient_appointment = pa.name
			INNER JOIN `tabItem` it ON ipd_cons.consultation_item = it.item_name
			LEFT OUTER JOIN `tabPatient Encounter` pe ON ipd_cons.encounter = pe.name
			LEFT OUTER JOIN `tabHealthcare Practitioner` hp ON pe.practitioner = hp.name
		WHERE ipd_rec.company = %(company)s
		AND ipd_rec.insurance_subscription != ""
        AND hicp.hms_tz_has_nhif_coverage = 0
		AND ipd_cons.date BETWEEN %(from_date)s AND %(to_date)s
		AND ipd_cons.is_confirmed = 1
		GROUP BY 
			YEAR(DATE(ipd_rec.admitted_datetime)),
			MONTHNAME(DATE(ipd_rec.admitted_datetime)),
			pe.practitioner,
            hp.healthcare_practitioner_type,
			pe.healthcare_service_unit,
			pa.coverage_plan_name,
			it.item_group
	""", filters, as_dict=1)
    return data


#NHIF patient appointment revenue
def get_nhif_appointment_revenue(filters):
	nhif_conditions = ''
	if filters.get("from_date"):
		nhif_conditions += " and Date(claim_doc.posting_date) >= %(from_date)s"
	if filters.get("to_date"):
		nhif_conditions += "and Date(claim_doc.posting_date) <= %(to_date)s"
	if filters.get("company"):
		nhif_conditions += "and claim_doc.company = %(company)s"
	
	data = frappe.db.sql("""
		SELECT 
            YEAR(claim_doc.posting_date) AS year,
            MONTHNAME(claim_doc.posting_date) AS month,
            pa.practitioner AS healthcare_practitioner,
            hp.healthcare_practitioner_type AS healthcare_practitioner_type,
            pa.service_unit AS practitioner_hsu,
            pa.service_unit AS department_hsu,
            SUM(claim_child.amount_claimed) AS amount,
            "Consultation" AS line_of_revenue,
            pa.coverage_plan_name AS payment_mode, 
            hp.department AS speciality,
            md.main_department AS main_department,
            "Submitted" AS status
        FROM `tabNHIF Patient Claim Item` claim_child
            INNER JOIN `tabNHIF Patient Claim` claim_doc ON claim_child.parent = claim_doc.name
            INNER JOIN `tabPatient Appointment` pa ON claim_child.ref_docname = pa.name
            INNER JOIN `tabHealthcare Practitioner` hp ON pa.practitioner = hp.name
            LEFT JOIN `tabMedical Department` md ON hp.department = md.name
        WHERE claim_doc.docstatus = 1 {nhif_conditions}
        GROUP BY 
            YEAR(claim_doc.posting_date), 
            MONTHNAME(claim_doc.posting_date), 
            pa.practitioner,
            hp.healthcare_practitioner_type,
            pa.service_unit, 
            pa.coverage_plan_name,
            hp.department,
            md.main_department
	""".format(nhif_conditions=nhif_conditions), filters, as_dict=1)
	return data

# NHIF LRPMT Revenue
def get_nhif_LRPMT_revenue(filters):
    nhif_conditions = ''
    if filters.get("from_date"):
        nhif_conditions += " and Date(claim_doc.posting_date) >= %(from_date)s"
    if filters.get("to_date"):
        nhif_conditions += "and Date(claim_doc.posting_date) <= %(to_date)s"
    if filters.get("company"):
        nhif_conditions += "and claim_doc.company = %(company)s"
    
    data = frappe.db.sql("""
        SELECT 
            YEAR(claim_doc.posting_date) AS year,
            MONTHNAME(claim_doc.posting_date) AS month,
            pe.practitioner AS healthcare_practitioner,
            hp.healthcare_practitioner_type AS healthcare_practitioner_type,
            pe.healthcare_service_unit AS practitioner_hsu, 
            hsp.department_hsu AS department_hsu,
            SUM(claim_child.amount_claimed) AS amount,
            "Lab" AS line_of_revenue, 
            pe.insurance_coverage_plan AS payment_mode, 
            hp.department AS speciality,
            md.main_department AS main_department,
            IF(MAX(hs_doc.docstatus) = 1, "Submitted", "Draft") AS status
        FROM `tabNHIF Patient Claim Item` claim_child
            INNER JOIN `tabNHIF Patient Claim` claim_doc ON claim_child.parent = claim_doc.name
            INNER JOIN `tabLab Prescription` hsp ON claim_child.ref_docname = hsp.name
            INNER JOIN `tabPatient Encounter` pe ON claim_child.patient_encounter = pe.name
            INNER JOIN `tabHealthcare Practitioner` hp ON pe.practitioner = hp.name
            LEFT JOIN `tabMedical Department` md ON hp.department = md.name
            LEFT OUTER JOIN `tabLab Test` hs_doc ON hsp.lab_test = hs_doc.name 
                AND hs_doc.docstatus IN (0, 1)
        WHERE claim_doc.docstatus =  1 {nhif_conditions}
        GROUP BY 
            YEAR(claim_doc.posting_date), 
            MONTHNAME(claim_doc.posting_date), 
            pe.practitioner,
            hp.healthcare_practitioner_type,
            pe.healthcare_service_unit, 
            hsp.department_hsu, 
            pe.insurance_coverage_plan,
            hp.department,
            md.main_department,
            hs_doc.docstatus
        
        UNION ALL

        SELECT 
            YEAR(claim_doc.posting_date) AS year, 
            MONTHNAME(claim_doc.posting_date) AS month, 
            pe.practitioner AS healthcare_practitioner,
            hp.healthcare_practitioner_type AS healthcare_practitioner_type,
            pe.healthcare_service_unit AS practitioner_hsu,
            hsp.department_hsu AS department_hsu, 
            SUM(claim_child.amount_claimed) AS amount, 
            "Radiology" AS line_of_revenue, 
            pe.insurance_coverage_plan AS payment_mode, 
            hp.department AS speciality,
            md.main_department AS main_department,
            IF(MAX(hs_doc.docstatus) = 1, "Submitted", "Draft") AS status
        FROM `tabNHIF Patient Claim Item` claim_child
            INNER JOIN `tabNHIF Patient Claim` claim_doc ON claim_child.parent = claim_doc.name
            INNER JOIN `tabRadiology Procedure Prescription` hsp ON claim_child.ref_docname = hsp.name
            INNER JOIN `tabPatient Encounter` pe ON claim_child.patient_encounter = pe.name
            INNER JOIN `tabHealthcare Practitioner` hp ON pe.practitioner = hp.name
            LEFT JOIN `tabMedical Department` md ON hp.department = md.name
            LEFT OUTER JOIN `tabRadiology Examination` hs_doc ON hsp.radiology_examination = hs_doc.name 
                AND hs_doc.docstatus IN (0, 1)
        WHERE claim_doc.docstatus =  1 {nhif_conditions}
        GROUP BY 
            YEAR(claim_doc.posting_date), 
            MONTHNAME(claim_doc.posting_date), 
            pe.practitioner,
            hp.healthcare_practitioner_type,
            pe.healthcare_service_unit, 
            hsp.department_hsu, 
            pe.insurance_coverage_plan,
            hp.department,
            md.main_department,
            hs_doc.docstatus
        
        UNION ALL

        SELECT 
            YEAR(claim_doc.posting_date) AS year, 
            MONTHNAME(claim_doc.posting_date) AS month,
            pe.practitioner AS healthcare_practitioner,
            hp.healthcare_practitioner_type AS healthcare_practitioner_type,
            pe.healthcare_service_unit AS practitioner_hsu, 
            hsp.department_hsu AS department_hsu, 
            SUM(claim_child.amount_claimed) AS amount, 
            "Clinical Procedure" AS line_of_revenue, 
            pe.insurance_coverage_plan AS payment_mode, 
            hp.department AS speciality,
            md.main_department AS main_department,
            IF(MAX(hs_doc.docstatus) = 1, "Submitted", "Draft") AS status
        FROM `tabNHIF Patient Claim Item` claim_child
            INNER JOIN `tabNHIF Patient Claim` claim_doc ON claim_child.parent = claim_doc.name
            INNER JOIN `tabProcedure Prescription` hsp ON claim_child.ref_docname = hsp.name
            INNER JOIN `tabPatient Encounter` pe ON claim_child.patient_encounter = pe.name
            INNER JOIN `tabHealthcare Practitioner` hp ON pe.practitioner = hp.name
            LEFT JOIN `tabMedical Department` md ON hp.department = md.name
            LEFT OUTER JOIN `tabClinical Procedure` hs_doc ON hsp.clinical_procedure = hs_doc.name
                AND hs_doc.docstatus IN (0, 1)
        WHERE claim_doc.docstatus =  1 {nhif_conditions}
        GROUP BY 
            YEAR(claim_doc.posting_date), 
            MONTHNAME(claim_doc.posting_date),
            pe.practitioner,
            hp.healthcare_practitioner_type,
            pe.healthcare_service_unit, 
            hsp.department_hsu, 
            pe.insurance_coverage_plan,
            hp.department,
            md.main_department,
            hs_doc.docstatus
        
        UNION ALL

        SELECT 
            YEAR(claim_doc.posting_date) AS year,
            MONTHNAME(claim_doc.posting_date) AS month,
            pe.practitioner AS healthcare_practitioner,
            hp.healthcare_practitioner_type AS healthcare_practitioner_type,
            pe.healthcare_service_unit AS practitioner_hsu,
            hsp.healthcare_service_unit  AS department_hsu,
            SUM(claim_child.amount_claimed) AS amount, 
            "Medication" AS line_of_revenue,
            pe.insurance_coverage_plan AS payment_mode, 
            hp.department AS speciality,
            md.main_department AS main_department,
            IF(MAX(hs_doc.docstatus) = 1, "Submitted", "Draft") AS status
        FROM `tabNHIF Patient Claim Item` claim_child
            INNER JOIN `tabNHIF Patient Claim` claim_doc ON claim_child.parent = claim_doc.name
            INNER JOIN `tabDrug Prescription` hsp ON claim_child.ref_docname = hsp.name
            INNER JOIN `tabPatient Encounter` pe ON claim_child.patient_encounter = pe.name
            INNER JOIN `tabHealthcare Practitioner` hp ON pe.practitioner = hp.name
            LEFT JOIN `tabMedical Department` md ON hp.department = md.name
            LEFT OUTER JOIN `tabDelivery Note Item` hs_doc ON hsp.name = hs_doc.reference_name 
                AND hs_doc.reference_doctype = "Drug Prescription" AND hs_doc.docstatus IN (0, 1)
            LEFT OUTER JOIN `tabDelivery Note` dn ON hs_doc.parent = dn.name AND dn.docstatus IN (0, 1)
                AND dn.is_return = 0 
        WHERE claim_doc.docstatus =  1 {nhif_conditions}
        GROUP BY 
            YEAR(claim_doc.posting_date), 
            MONTHNAME(claim_doc.posting_date),
            pe.practitioner,
            hp.healthcare_practitioner_type,
            pe.healthcare_service_unit, 
            hsp.healthcare_service_unit,
            pe.insurance_coverage_plan,
            hp.department,
            md.main_department,
            hs_doc.docstatus
        
        UNION ALL

        SELECT 
            YEAR(claim_doc.posting_date) AS year,
            MONTHNAME(claim_doc.posting_date) AS month,
            pe.practitioner AS healthcare_practitioner,
            hp.healthcare_practitioner_type AS healthcare_practitioner_type,
            pe.healthcare_service_unit AS practitioner_hsu,
            hsp.department_hsu AS department_hsu,
            SUM(claim_child.amount_claimed) AS amount,
            "Therapy" AS line_of_revenue,
            pe.insurance_coverage_plan AS payment_mode, 
            hp.department AS speciality,
            md.main_department AS main_department,
            IF(1 = 1, "Submitted", "Draft") AS status
        FROM `tabNHIF Patient Claim Item` claim_child
            INNER JOIN `tabNHIF Patient Claim` claim_doc ON claim_child.parent = claim_doc.name
            INNER JOIN `tabTherapy Plan Detail` hsp ON claim_child.ref_docname = hsp.name
            INNER JOIN `tabPatient Encounter` pe ON claim_child.patient_encounter = pe.name
            INNER JOIN `tabHealthcare Practitioner` hp ON pe.practitioner = hp.name
            LEFT JOIN `tabMedical Department` md ON hp.department = md.name
        WHERE claim_doc.docstatus =  1 {nhif_conditions}
        GROUP BY 
            YEAR(claim_doc.posting_date), 
            MONTHNAME(claim_doc.posting_date),
            pe.practitioner,
            hp.healthcare_practitioner_type,
            pe.healthcare_service_unit,
            hsp.department_hsu,
            pe.insurance_coverage_plan, 
            hp.department,
            md.main_department, 1
    """.format(nhif_conditions=nhif_conditions), filters, as_dict=1)
    return data

# NHIF Inpatient Revenue(occupancy and consultancy)
def get_nhif_inpatient_revenue(filters):
    nhif_conditions = ''
    if filters.get("from_date"):
        nhif_conditions += " and Date(claim_doc.posting_date) >= %(from_date)s"
    if filters.get("to_date"):
        nhif_conditions += "and Date(claim_doc.posting_date) <= %(to_date)s"
    if filters.get("company"):
        nhif_conditions += "and claim_doc.company = %(company)s"
    
    data = frappe.db.sql("""
        SELECT 
            YEAR(claim_doc.posting_date) AS year,
            MONTHNAME(claim_doc.posting_date) AS month,
            null AS healthcare_practitioner,
            null AS healthcare_practitioner_type,
            null AS practitioner_hsu,
            claim_child.item_name AS department_hsu,
            SUM(claim_child.amount_claimed) AS amount, 
            "IPD" AS line_of_revenue,
            pe.insurance_coverage_plan AS payment_mode,
            hsut.item_group AS speciality,
            null AS main_department,
            "Confirmed" AS status
        FROM `tabNHIF Patient Claim Item` claim_child
            INNER JOIN `tabNHIF Patient Claim` claim_doc ON claim_child.parent = claim_doc.name
            INNER JOIN `tabInpatient Occupancy` ipd_occ ON claim_child.ref_docname = ipd_occ.name
            INNER JOIN `tabHealthcare Service Unit` hsu ON claim_child.item_name = hsu.name
            INNER JOIN `tabHealthcare Service Unit Type` hsut ON hsu.service_unit_type = hsut.name
            INNER JOIN `tabPatient Encounter` pe ON claim_child.patient_encounter = pe.name
        WHERE claim_doc.docstatus =  1 {nhif_conditions}
        GROUP BY 
            YEAR(claim_doc.posting_date),
            MONTHNAME(claim_doc.posting_date),
            claim_child.item_name,
            hsut.item_group,
            pe.insurance_coverage_plan
        
        UNION ALL

        SELECT 
            YEAR(claim_doc.posting_date) AS year,
            MONTHNAME(claim_doc.posting_date) AS month,
            pe.practitioner AS healthcare_practitioner,
            hp.healthcare_practitioner_type AS healthcare_practitioner_type,
            pe.healthcare_service_unit AS practitioner_hsu, 
            null AS department_hsu,
            SUM(claim_child.amount_claimed) AS amount, 
            "IPD" AS line_of_revenue,
            pe.insurance_coverage_plan AS payment_mode,
            it.item_group AS speciality, 
            null AS main_department, "Confirmed" AS status
        FROM `tabNHIF Patient Claim Item` claim_child
            INNER JOIN `tabNHIF Patient Claim` claim_doc ON claim_child.parent = claim_doc.name
            INNER JOIN `tabInpatient Consultancy` ipd_cons ON claim_child.ref_docname = ipd_cons.name
            INNER JOIN `tabPatient Encounter` pe ON claim_child.patient_encounter = pe.name
            INNER JOIN `tabHealthcare Practitioner` hp ON pe.practitioner = hp.name
            INNER JOIN `tabItem` it ON claim_child.item_name = it.name
        WHERE claim_doc.docstatus =  1 {nhif_conditions}
        GROUP BY 
            YEAR(claim_doc.posting_date),
            MONTHNAME(claim_doc.posting_date),
            pe.practitioner,
            hp.healthcare_practitioner_type,
            pe.healthcare_service_unit,
            pe.insurance_coverage_plan,
            it.item_group
    """.format(nhif_conditions=nhif_conditions), filters, as_dict=1)
    return data

# Cash transactions
# Appointments, labs, radiologies, procudures, drugs, therapies, 
# ipd occupancy, ipd consultancies and other sales
def get_cash_transactions(filters):
    conditions = ""
    if filters.get("from_date"):
        conditions += "AND si.posting_date >= %(from_date)s"
    if filters.get("to_date"):
        conditions += "AND si.posting_date <= %(to_date)s"
    if filters.get("company"):
        conditions += "AND si.company = %(company)s"

    data = frappe.db.sql(
        """
		SELECT
			YEAR(si.posting_date) AS year,
			MONTHNAME(si.posting_date) AS month,
			sii.healthcare_practitioner AS healthcare_practitioner, 
			null AS practitioner_hsu,
			sii.healthcare_service_unit AS department_hsu,
			SUM(sii.amount) AS amount,
			sii.item_group AS department,
			"Cash" AS payment_mode,
			null AS speciality,
			null AS main_department,
			"Submitted" AS status
		FROM `tabSales Invoice Item` sii
		INNER JOIN `tabSales Invoice` si ON sii.parent = si.name
		WHERE si.is_pos = 1
		AND sii.docstatus = 1 {conditions}
		GROUP BY
			YEAR(si.posting_date),
			MONTHNAME(si.posting_date),
			sii.healthcare_practitioner,
			sii.healthcare_service_unit,
			sii.item_group

		UNION  ALL

		SELECT
			YEAR(si.posting_date) AS year,
			MONTHNAME(si.posting_date) AS month,
			sii.healthcare_practitioner AS healthcare_practitioner, 
			null AS practitioner_hsu,
			sii.healthcare_service_unit AS department_hsu,
			SUM(sii.amount) AS amount,
			sii.item_group AS department,
			"Cash" AS payment_mode,
			null AS speciality,
			null AS main_department,
			"Submitted" AS status
		FROM `tabSales Invoice Item` sii
		INNER JOIN `tabSales Invoice` si ON sii.parent = si.name
		WHERE si.is_pos = 0
		AND si.patient != ""
		AND sii.docstatus = 1 {conditions}
		GROUP BY
			YEAR(si.posting_date),
			MONTHNAME(si.posting_date),
			sii.healthcare_practitioner,
			sii.healthcare_service_unit,
			sii.item_group
	""".format(conditions=conditions), filters, as_dict=1,
    )
    return data