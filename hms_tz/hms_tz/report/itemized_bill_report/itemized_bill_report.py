# Copyright (c) 2022, Aakvatech and contributors
# For license information, please see license.txt

from concurrent.futures import thread
import frappe
from frappe import _
from frappe.utils import cint, flt
from erpnext.accounts.utils import get_balance_on


def execute(filters=None):
    if not filters:
        return

    columns = get_columns(filters)

    data = []
    details = frappe.get_all(
        "Patient Appointment",
        filters=[
            ["patient", "=", filters.patient],
            ["name", "=", filters.patient_appointment],
        ],
        fields=[
            "docstatus",
            "status",
        ],
    )

    if details[0]["docstatus"] == 0 and details[0]["status"] != "Closed":
        frappe.throw(frappe.bold("This Appointment is not Closed..!!"))

    else:
        if not filters.get("patient_type"):
            appointments_data = get_appointment_consultancy(filters)
            if appointments_data:
                data += appointments_data

            cash_lrpmt_data = get_cash_lrpmt_transaction(filters)
            if cash_lrpmt_data:
                data += cash_lrpmt_data

            insurance_lrpmt_data = get_insurance_lrpmt_transaction(filters)
            if insurance_lrpmt_data:
                data += insurance_lrpmt_data

            ipd_beds = get_ipd_occupancy_transactions(filters)
            if ipd_beds:
                data += ipd_beds

            ipd_cons = get_ipd_consultancy_transactions(filters)
            if ipd_cons:
                data += ipd_cons

            data = sorted(data, key=lambda d: (d["category"], d["date"]))

            if not data:
                frappe.throw(
                    "No Record found for the filters Patient: {0}, Appointment: {1},\
					Patient Type: {2} From Date: {3} and To Date: {4} you specified..., \
					Please change your filters and try again..!!".format(
                        frappe.bold(filters.patient),
                        frappe.bold(filters.patient_appointment),
                        frappe.bold(filters.patient_type),
                        frappe.bold(filters.from_date),
                        frappe.bold(filters.to_date),
                    )
                )

            total_amount = 0
            for n in range(0, len(data)):
                total_amount += data[n]["amount"]

            last_row = {
                "date": "Total",
                "category": "",
                "description": "",
                "quantity": "",
                "rate": "",
                "amount": total_amount,
                "patient": "",
                "patient_name": "",
                "appointment_type": "",
                "insurance_company": "",
                "coverage_plan_name": "",
                "authorization_number": "",
                "coverage_plan_card_number": "",
                "admitted_date": "",
                "discharge_date": "",
            }

            print_person = frappe.get_value("User", frappe.session.user, "full_name")

            last_row["printed_by"] = print_person

            data.append(last_row)

            return columns, data

        if filters.get("patient_type") == "Out-Patient":
            appointments_data = get_appointment_consultancy(filters)
            if appointments_data:
                data += appointments_data

            cash_lrpmt_data = get_cash_lrpmt_transaction(filters)
            if cash_lrpmt_data:
                data += cash_lrpmt_data

            insurance_lrpmt_data = get_insurance_lrpmt_transaction(filters)
            if insurance_lrpmt_data:
                data += insurance_lrpmt_data

            data = sorted(data, key=lambda d: (d["category"], d["date"]))

            if not data:
                frappe.throw(
                    "No Record found for the filters Patient: {0}, Appointment: {1},\
					Patient Type: {2} From Date: {3} and To Date: {4} you specified..., \
					Please change your filters and try again..!!".format(
                        frappe.bold(filters.patient),
                        frappe.bold(filters.patient_appointment),
                        frappe.bold(filters.patient_type),
                        frappe.bold(filters.from_date),
                        frappe.bold(filters.to_date),
                    )
                )

            total_amount = 0
            for n in range(0, len(data)):
                total_amount += data[n]["amount"]

            last_row = {
                "date": "Total",
                "category": "",
                "description": "",
                "quantity": "",
                "rate": "",
                "amount": total_amount,
                "patient": "",
                "patient_name": "",
                "appointment_type": "",
                "insurance_company": "",
                "coverage_plan_name": "",
                "authorization_number": "",
                "coverage_plan_card_number": "",
                "admitted_date": "",
                "discharge_date": "",
            }

            print_person = frappe.get_value("User", frappe.session.user, "full_name")

            last_row["printed_by"] = print_person

            data.append(last_row)

            return columns, data

        if filters.get("patient_type") == "In-Patient":
            cash_lrpmt_data = get_cash_lrpmt_transaction(filters)
            if cash_lrpmt_data:
                data += cash_lrpmt_data

            insurance_lrpmt_data = get_insurance_lrpmt_transaction(filters)
            if insurance_lrpmt_data:
                data += insurance_lrpmt_data

            ipd_beds = get_ipd_occupancy_transactions(filters)
            if ipd_beds:
                data += ipd_beds

            ipd_cons = get_ipd_consultancy_transactions(filters)
            if ipd_cons:
                data += ipd_cons

            data = sorted(data, key=lambda d: (d["category"], d["date"]))
            if not data:
                frappe.throw(
                    "No Record found for the filters Patient: {0}, Appointment: {1},\
					Patient Type: {2} From Date: {3} and To Date: {4} you specified..., \
					Please change your filters and try again..!!".format(
                        frappe.bold(filters.patient),
                        frappe.bold(filters.patient_appointment),
                        frappe.bold(filters.patient_type),
                        frappe.bold(filters.from_date),
                        frappe.bold(filters.to_date),
                    )
                )

            total_amount = 0
            for n in range(0, len(data)):
                total_amount += data[n]["amount"]

            last_row = {
                "date": "Total",
                "category": "",
                "description": "",
                "quantity": "",
                "rate": "",
                "amount": total_amount,
                "patient": "",
                "patient_name": "",
                "appointment_type": "",
                "insurance_company": "",
                "coverage_plan_name": "",
                "authorization_number": "",
                "coverage_plan_card_number": "",
                "admitted_date": "",
                "discharge_date": "",
            }

            print_person = frappe.get_value("User", frappe.session.user, "full_name")

            last_row["printed_by"] = print_person

            data.append(last_row)
            # summary_view = get_report_summary(filters, total_amount)

            return columns, data  # , None, None, summary_view


def get_columns(filters):
    columns = [
        {"fieldname": "date", "fieldtype": "date", "label": _("Date")},
        {"fieldname": "category", "fieldtype": "Data", "label": _("Category")},
        {"fieldname": "description", "fieldtype": "Data", "label": _("Description")},
        {"fieldname": "quantity", "fieldtype": "Data", "label": _("Quantity")},
        {"fieldname": "rate", "fieldtype": "Currency", "label": _("Rate")},
        {"fieldname": "amount", "fieldtype": "Currency", "label": _("Amount")},
    ]
    return columns


def get_conditions(filters):
    if filters.get("patient"):
        conditions = "and pa.patient = %(patient)s"

    if filters.get("patient_appointment"):
        conditions += "and pa.name = %(patient_appointment)s"

    if filters.get("from_date"):
        conditions += " and pa.appointment_date >= %(from_date)s"

    if filters.get("to_date"):
        conditions += " and pa.appointment_date <= %(to_date)s"

    return conditions


def get_enc_conditions(filters):
    if filters.get("patient"):
        conditions = " and pe.patient = %(patient)s"

    if filters.get("patient_appointment"):
        conditions += " and pe.appointment = %(patient_appointment)s"

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

    if filters.get("patient_appointment"):
        conditions += " and ipd_rec.patient_appointment = %(patient_appointment)s"

    if filters.get("from_date"):
        conditions += " and DATE(ipd_rec.admitted_datetime) >= %(from_date)s"

    if filters.get("to_date"):
        conditions += " and DATE(ipd_rec.admitted_datetime) <= %(to_date)s"

    return conditions


def get_appointment_consultancy(filters):
    conditions = get_conditions(filters)

    data = frappe.db.sql(
        """
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
	""".format(
            conditions=conditions
        ),
        filters,
        as_dict=1,
    )
    return data


def get_ipd_occupancy_transactions(filters):
    ipd_conditions = get_ipd_conditions(filters)
    pe_conditions = get_enc_conditions(filters)

    data = frappe.db.sql(
        """
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
	""".format(
            pe_conditions=pe_conditions, ipd_conditions=ipd_conditions
        ),
        filters,
        as_dict=1,
    )

    return data


def get_ipd_consultancy_transactions(filters):
    ipd_conditions = get_ipd_conditions(filters)
    pe_conditions = get_enc_conditions(filters)

    data = frappe.db.sql(
        """
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
	""".format(
            pe_conditions=pe_conditions, ipd_conditions=ipd_conditions
        ),
        filters,
        as_dict=1,
    )
    return data


def get_cash_lrpmt_transaction(filters):
    conditions = get_enc_conditions(filters)

    data = frappe.db.sql(
        """
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
	""".format(
            conditions=conditions
        ),
        filters,
        as_dict=1,
    )

    return data


def get_insurance_lrpmt_transaction(filters):
    conditions = get_enc_conditions(filters)

    data = frappe.db.sql(
        """
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
	""".format(
            conditions=conditions
        ),
        filters,
        as_dict=1,
    )

    return data


def get_report_summary(filters, total_amount):
    customer = frappe.get_value("Patient", filters.get("patient"), "customer")
    company = frappe.get_value(
        "Patient Appointment", filters.get("patient_appointment"), "company"
    )

    deposit_balance = -1 * get_balance_on(
        party_type="Customer", party=customer, company=company
    )

    current_balance = flt(flt(deposit_balance) - flt(total_amount))

    currency = frappe.get_cached_value("Company", company, "default_currency")

    return [
        {
            "value": deposit_balance,
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
