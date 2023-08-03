# Copyright (c) 2022, Aakvatech and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.utils import cint, flt
from frappe.query_builder import DocType as dt
from frappe.query_builder.functions import Sum, Count
from pypika import Case



def execute(filters=None):
    if not filters:
        return

<<<<<<< HEAD
    columns = [
        {
            "fieldname": "practitioner",
            "fieldtype": "Data",
            "label": _("Healthcare Practitioner"),
        },
        {"fieldname": "billing_item", "fieldtype": "Data", "label": _("Item")},
        {"fieldname": "patients", "fieldtype": "Data", "label": _("Patients")},
        {"fieldname": "mode", "fieldtype": "Data", "label": _("Mode")},
=======
    commission_doc, excluded_services_map = get_commission_doc(filters)
    data = get_lab_commissions(filters, commission_doc, excluded_services_map)
    # data = get_appointment_consultancy(filters, visiting_rates)

    # visiting_rates = frappe.get_all(
    #     "Visiting Rate",
    #     filters={"parent": commission_name[0].name},
    #     fields=["funding_provider", "document_type", "vc_rate", "company_rate"],
    # )

    # excluded_service_rates = frappe.get_all(
    #     "Excluded Service Rate",
    #     filters={"parent": commission_name[0].name},
    #     fields=["document_type", "service", "vc_rate", "company_rate"],
    # )

    columns = get_columns(filters)

    # data += get_procedure_consultancy(filters, visiting_rates, excluded_service_rates)

    return columns, data


def get_columns(filters):
    columns = []
    if filters.get("practitioner") and not filters.get("vc_technician"):
        columns.append(
            {
                "fieldname": "practitioner",
                "fieldtype": "Data",
                "label": _("Healthcare Practitioner"),
                "width": "160px",
            }
        )
    elif filters.get("vc_technician") and not filters.get("practitioner"):
        columns.append(
            {
                "fieldname": "vc_technician",
                "fieldtype": "Data",
                "label": _("VC Technician"),
                "width": "160px",
            }
        )
    else:
        columns += [
            {
                "fieldname": "practitioner",
                "fieldtype": "Data",
                "label": _("Healthcare Practitioner"),
                "width": "160px",
            },
            {
                "fieldname": "vc_technician",
                "fieldtype": "Data",
                "label": _("VC Technician"),
                "width": "160px",
            },
        ]
    columns += [
        {
            "fieldname": "billing_item",
            "fieldtype": "Data",
            "label": _("Item"),
            "width": "160px",
        },
        {
            "fieldname": "no_of_patients",
            "fieldtype": "Int",
            "label": _("Patient Count"),
            "width": "100px",
        },
        {
            "fieldname": "no_of_tests",
            "fieldtype": "Int",
            "label": _("Test Count"),
            "width": "100px",
        },
        {
            "fieldname": "mode",
            "fieldtype": "Data",
            "label": _("Mode"),
            "width": "160px",
        },
>>>>>>> a6711458 (feat: show cash and insurance vc rates for lab records)
        {
            "fieldname": "paid_amount",
            "fieldtype": "Currency",
            "label": _("Paid Amount"),
<<<<<<< HEAD
        },
        {"fieldname": "vc_amount", "fieldtype": "Currency", "label": _("Vc Amount")},
=======
            "width": "120px",
        },
        {
            "fieldname": "vc_amount",
            "fieldtype": "Currency",
            "label": _("Vc Amount"),
            "width": "120px",
        },
>>>>>>> a6711458 (feat: show cash and insurance vc rates for lab records)
        {
            "fieldname": "company_amount",
            "fieldtype": "Currency",
            "label": _("Company Amount"),
<<<<<<< HEAD
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
=======
            "width": "120px",
        },
    ]
    return columns


def get_commission_doc(filters):
    insurance_rates = []
    cash_rates = []
    excluded_rates = []
    vc_lab_users = []
    vc_radiology_users = []

    commission_list = frappe.get_all(
        "Visiting Comission",
        filters={
            "company": filters.get("company"),
            "valid_from": ["<=", filters.get("to_date")],
        },
        fields=["name"],
        order_by="valid_from desc",
        limit=1,
    )
    commission_doc = frappe.get_doc("Visiting Comission", commission_list[0].name)
    excluded_services_map = {}
    for row in commission_doc.excluded_service_rates:
        excluded_services_map.setdefault(row.document_type, []).append(
            row.healthcare_service
        )

    return commission_doc, excluded_services_map
>>>>>>> a6711458 (feat: show cash and insurance vc rates for lab records)


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
<<<<<<< HEAD
=======


def get_lab_commissions(filters, commission_doc, excluded_services_map):
    lab_test = dt("Lab Test")
    prescription = dt("Lab Prescription")
    case_wh = None
    if filters.get("vc_technician"):
        case_wh = lab_test.hms_tz_user_id == filters.get("vc_technician")
    else:
        case_wh = lab_test.hms_tz_user_id != ""

    lab_records = (
        frappe.qb.from_(lab_test)
        .inner_join(prescription)
        .on(
            lab_test.hms_tz_ref_childname == prescription.name
            and lab_test.ref_docname == prescription.parent
        )
        .select(
            lab_test.template,
            lab_test.hms_tz_submitted_by,
            lab_test.hms_tz_user_id,
            prescription.prescribe,
            Sum(prescription.amount).as_("amount"),
            Count(lab_test.patient).distinct().as_("no_of_patients"),
            Count(lab_test.template).as_("no_of_tests"),
            Case()
            .when(prescription.prescribe == 0, lab_test.hms_tz_insurance_coverage_plan)
            .else_("CASH")
            .as_("mode"),
        )
        .where(
            (lab_test.ref_doctype == "Patient Encounter")
            & (lab_test.ref_docname == prescription.parent)
            & (lab_test.hms_tz_ref_childname == prescription.name)
            & (lab_test.docstatus == 1)
        )
        .where(
            (
                (lab_test.submitted_date >= filters.get("from_date"))
                & (lab_test.submitted_date <= filters.get("to_date"))
                & (lab_test.company == filters.get("company"))
                & case_wh
            )
        )
        .groupby(
            Case()
            .when(prescription.prescribe == 0, lab_test.hms_tz_insurance_coverage_plan)
            .else_("CASH")
            .as_("mode"),
            lab_test.hms_tz_user_id,
            lab_test.template,
        )
    ).run(as_dict=1)

    lab_list = []
    excluded_lab_tests = []
    for row in lab_records:
        if row.template in excluded_services_map.get("Lab Test", []):
            excluded_lab_tests.append(row)
        elif row.prescribe == 1 and row.mode == "CASH":
            for rate_row in commission_doc.cash_rates:
                if rate_row.document_type == "Lab Test":
                    lab_list.append(
                        {
                            "practitioner": "",
                            "vc_technician": row.hms_tz_submitted_by,
                            "billing_item": row.template,
                            "no_of_patients": row.no_of_patients,
                            "no_of_tests": row.no_of_tests,
                            "mode": row.mode,
                            "paid_amount": row.amount,
                            "vc_amount": flt(row.amount * flt(rate_row.vc_rate / 100)),
                            "company_amount": flt(
                                row.amount * flt(rate_row.company_rate / 100)
                            ),
                        }
                    )
        elif row.prescribe == 0 and row.mode != "CASH":
            coverage_plan = frappe.get_cached_value(
                "Healthcare Insurance Coverage Plan",
                {"coverage_plan_name": row.mode},
                "name",
            )
            for rate_row in commission_doc.insurance_rates:
                if (
                    rate_row.coverage_plan == coverage_plan
                    and rate_row.document_type == "Lab Test"
                ):
                    lab_list.append(
                        {
                            "practitioner": "",
                            "vc_technician": row.hms_tz_submitted_by,
                            "billing_item": row.template,
                            "no_of_patients": row.no_of_patients,
                            "no_of_tests": row.no_of_tests,
                            "mode": row.mode,
                            "paid_amount": row.amount,
                            "vc_amount": flt(row.amount * flt(rate_row.vc_rate / 100)),
                            "company_amount": flt(
                                row.amount * flt(rate_row.company_rate / 100)
                            ),
                        }
                    )
    return lab_list
>>>>>>> a6711458 (feat: show cash and insurance vc rates for lab records)


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
