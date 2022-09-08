# Copyright (c) 2022, Aakvatech and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.utils import cint, flt


def execute(filters=None):
    if not filters:
        return

    columns = [
        {
            "fieldname": "practitioner",
            "fieldtype": "Data",
            "label": _("Healthcare Practitioner"),
        },
        {"fieldname": "billing_item", "fieldtype": "Data", "label": _("Item")},
        {"fieldname": "patients", "fieldtype": "Data", "label": _("Patients")},
        {"fieldname": "mode", "fieldtype": "Data", "label": _("Mode")},
        {
            "fieldname": "paid_amount",
            "fieldtype": "Currency",
            "label": _("Paid Amount"),
        },
        {"fieldname": "vc_amount", "fieldtype": "Currency", "label": _("Vc Amount")},
        {
            "fieldname": "company_amount",
            "fieldtype": "Currency",
            "label": _("Company Amount"),
        },
    ]

    commission_name = frappe.get_all("Visiting Comission")

    visiting_rates = frappe.get_all(
        "Visiting Rate",
        filters={"parent": commission_name[0].name},
        fields=["funding_provider", "document_type", "vc_rate", "company_rate"],
    )

    excluded_service_rates = frappe.get_all(
        "Excluded Service Rate",
        filters={"parent": commission_name[0].name},
        fields=["document_type", "service", "vc_rate", "company_rate"],
    )

    data = get_appointment_consultancy(filters, visiting_rates)
    data += get_procedure_consultancy(filters, visiting_rates, excluded_service_rates)

    return columns, data


def get_appointment_consultancy(filters, visiting_rates):
    conditions = ""
    if filters.get("from_date") and filters.get("to_date"):
        conditions += (
            " AND Date(pa.appointment_date) between %(from_date)s and %(to_date)s"
        )

    if filters.get("company"):
        conditions += " AND pa.company = %(company)s"
        conditions += " AND pe.company = %(company)s"

    if filters.get("practitioner"):
        conditions += " AND pa.practitioner = %(practitioner)s"
        conditions += " AND pe.practitioner = %(practitioner)s"

    records = frappe.db.sql(
        """
		SELECT COUNT(pa.patient) AS patients, pa.billing_item, SUM(pa.paid_amount) AS paid_amount,
			pa.practitioner, if(pa.insurance_company != "", pa.insurance_company, "CASH OPD") AS mode,
			"Patient Appointment" AS pa_doc
		FROM `tabPatient Appointment` pa
		INNER JOIN `tabPatient Encounter` pe ON pa.name = pe.appointment
		WHERE pa.status = "Closed"
		AND pa.follow_up = 0
		AND pe.encounter_type = "Final"
		AND pe.duplicated = 0 {conditions}
		GROUP BY pa.practitioner, mode, pa.billing_item
	""".format(
            conditions=conditions
        ),
        filters,
        as_dict=1,
    )

    consultancies = []
    for record in records:
        for rate_category in visiting_rates:
            if (
                record.mode == "NHIF"
                and record.pa_doc == rate_category.document_type
                and record.mode == rate_category.funding_provider
            ):
                vc_amount = flt(record.paid_amount * flt(rate_category.vc_rate / 100))
                company_amount = flt(
                    record.paid_amount * flt(rate_category.company_rate / 100)
                )
                record.update(
                    {"vc_amount": vc_amount, "company_amount": company_amount}
                )

                consultancies.append(record)

            if (
                record.mode != "NHIF"
                and record.pa_doc == rate_category.document_type
                and rate_category.funding_provider == "Other"
            ):
                vc_amount = flt(record.paid_amount * flt(rate_category.vc_rate / 100))
                company_amount = flt(
                    record.paid_amount * flt(rate_category.company_rate / 100)
                )
                record.update(
                    {"vc_amount": vc_amount, "company_amount": company_amount}
                )

                consultancies.append(record)

    return consultancies


def get_procedure_consultancy(filters, visiting_rates, excluded_service_rates):
    conditions = ""
    if filters.get("from_date") and filters.get("to_date"):
        conditions += " AND cp.start_date between %(from_date)s and %(to_date)s"

    if filters.get("company"):
        conditions += " AND cp.company = %(company)s"

    if filters.get("practitioner"):
        conditions += " AND cp.practitioner = %(practitioner)s"

    procedures = frappe.db.sql(
        """
		SELECT cp.practitioner, cp.procedure_template AS billing_item,
		cp.insurance_company AS mode, SUM(pp.amount) AS paid_amount,
		COUNT(cp.patient) AS patients, "Clinical Procedure" AS cl_doc
		FROM `tabClinical Procedure` cp
		INNER JOIN `tabProcedure Prescription` pp ON cp.ref_docname = pp.parent
			AND cp.procedure_template = pp.procedure AND pp.prescribe = 0
		WHERE cp.insurance_company != ""
		AND cp.status = "Completed" {conditions}
		GROUP BY mode, cp.procedure_template, cp.practitioner

		UNION ALL

		SELECT cp.practitioner, cp.procedure_template AS billing_item,
		"CASH PROCEDURE" AS mode, SUM(pp.amount) AS paid_amount,
		COUNT(cp.patient) AS patients, "Clinical Procedure" AS cl_doc
		FROM `tabClinical Procedure` cp
		INNER JOIN `tabProcedure Prescription` pp ON cp.ref_docname = pp.parent
			AND cp.procedure_template = pp.procedure AND pp.prescribe = 1
		WHERE cp.insurance_company is null
		AND cp.status = "Completed"  {conditions}
		GROUP BY cp.practitioner, mode, cp.procedure_template
	""".format(
            conditions=conditions
        ),
        filters,
        as_dict=1,
    )

    service_list = []
    excluded_list = []

    for procedure in procedures:
        for excluded_service in excluded_service_rates:
            if excluded_service.service not in excluded_list:
                excluded_list.append(excluded_service.service)

            if (
                procedure.cl_doc == excluded_service.document_type
                and procedure.billing_item == excluded_service.service
            ):
                paid_amount = procedure.paid_amount or 0

                vc_amount = flt(paid_amount * flt(excluded_service.vc_rate / 100))
                company_amount = flt(
                    paid_amount * flt(excluded_service.company_rate / 100)
                )

                procedure.update(
                    {
                        "paid_amount": paid_amount,
                        "vc_amount": vc_amount,
                        "company_amount": company_amount,
                    }
                )

                service_list.append(procedure)

        if procedure.billing_item in excluded_list:
            continue

        else:
            for rate_category in visiting_rates:
                if (
                    procedure.mode == "NHIF"
                    and procedure.cl_doc == rate_category.document_type
                    and procedure.mode == rate_category.funding_provider
                ):
                    paid_amount = procedure.paid_amount or 0

                    vc_amount = flt(paid_amount * flt(rate_category.vc_rate / 100))
                    company_amount = flt(
                        paid_amount * flt(rate_category.company_rate / 100)
                    )

                    procedure.update(
                        {
                            "paid_amount": paid_amount,
                            "vc_amount": vc_amount,
                            "company_amount": company_amount,
                        }
                    )

                    service_list.append(procedure)

                if (
                    procedure.mode != "NHIF"
                    and procedure.cl_doc == rate_category.document_type
                    and rate_category.funding_provider == "Other"
                ):
                    paid_amount = procedure.paid_amount or 0

                    vc_amount = flt(paid_amount * flt(rate_category.vc_rate / 100))
                    company_amount = flt(
                        paid_amount * flt(rate_category.company_rate / 100)
                    )

                    procedure.update(
                        {
                            "paid_amount": paid_amount,
                            "vc_amount": vc_amount,
                            "company_amount": company_amount,
                        }
                    )

                    service_list.append(procedure)

    return service_list
