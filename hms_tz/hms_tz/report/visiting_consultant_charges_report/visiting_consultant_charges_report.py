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
=======
    data = []
>>>>>>> 256f8fd7 (feat: show cash and insurance vc rates for radiology, procedure and opd appointments)

    (
        commission_doc,
        excluded_services_map,
        vc_lab_users,
        vc_radiology_users,
    ) = get_commission_doc_details(filters)

    data += get_opd_commissions(
        filters, commission_doc.cash_rates, commission_doc.insurance_rates
    )
    data += get_procedure_commissions(
        filters,
        commission_doc.cash_rates,
        commission_doc.insurance_rates,
        excluded_services_map,
    )
    data += get_lab_commissions(
        filters,
        commission_doc.cash_rates,
        commission_doc.insurance_rates,
        excluded_services_map,
        vc_lab_users,
    )
    data += get_radiology_commissions(
        filters,
        commission_doc.cash_rates,
        commission_doc.insurance_rates,
        excluded_services_map,
        vc_radiology_users,
    )
    if len(data) == 0:
        frappe.msgprint("No records found")
        return []

    columns = get_columns(filters)
    dashboard = get_report_summary(filters, data)

    # return columns, data
    return columns, data, None, None, dashboard


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
            "fieldname": "patient_count",
            "fieldtype": "Int",
            "label": _("Patient Count"),
            "width": "100px",
        },
        {
            "fieldname": "item_count",
            "fieldtype": "Int",
            "label": _("Item Count"),
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


def get_commission_doc_details(filters):
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
        excluded_services_map.setdefault(row.document_type, []).append(row)

<<<<<<< HEAD
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
=======
    vc_lab_users = [row.user_field for row in commission_doc.lab_users]
    vc_radiology_users = [row.user_field for row in commission_doc.radiology_users]

    return commission_doc, excluded_services_map, vc_lab_users, vc_radiology_users


def get_opd_commissions(filters, cash_rates, insurance_rates):
>>>>>>> 256f8fd7 (feat: show cash and insurance vc rates for radiology, procedure and opd appointments)
    if filters.get("vc_technician"):
        return []

    appointment = dt("Patient Appointment")
    encounter = dt("Patient Encounter")
    case_wh = None
    if filters.get("practitioner"):
        case_wh = appointment.practitioner == filters.get("practitioner")
    else:
        case_wh = appointment.practitioner.isnotnull()

    appointment_records = (
        frappe.qb.from_(appointment)
        .inner_join(encounter)
        .on(appointment.name == encounter.appointment)
        .select(
            appointment.practitioner,
            appointment.billing_item,
            appointment.coverage_plan_name,
            appointment.insurance_subscription,
            appointment.paid_amount,
            Sum(appointment.paid_amount).as_("amount"),
            Count(appointment.patient).distinct().as_("patient_count"),
            Count(appointment.billing_item).as_("item_count"),
            Case()
            .when(
                appointment.insurance_subscription != "", appointment.coverage_plan_name
            )
            .else_("CASH")
            .as_("mode"),
        )
        .where(
            (appointment.status == "Closed")
            & (appointment.follow_up == 0)
            & (encounter.follow_up == 0)
            & (encounter.duplicated == 0)
            & (encounter.encounter_type == "Final")
        )
        .where(
            (
                (appointment.appointment_date >= filters.get("from_date"))
                & (appointment.appointment_date <= filters.get("to_date"))
                & (appointment.company == filters.get("company"))
                & case_wh
            )
        )
        .groupby(
            Case()
            .when(
                appointment.insurance_subscription != "", appointment.coverage_plan_name
            )
            .else_("CASH")
            .as_("mode"),
            appointment.practitioner,
            appointment.billing_item,
        )
    ).run(as_dict=1)

    appointment_list = []
    for row in appointment_records:
        if row.mode == "CASH":
            for rate_row in cash_rates:
                if rate_row.document_type == "Patient Appointment":
                    appointment_list.append(
                        {
                            "practitioner": row.practitioner,
                            "vc_technician": "",
                            "billing_item": row.billing_item,
                            "patient_count": row.patient_count,
                            "item_count": row.item_count,
                            "mode": row.mode,
                            "paid_amount": row.amount,
                            "vc_amount": flt(row.amount * flt(rate_row.vc_rate / 100)),
                            "company_amount": flt(
                                row.amount * flt(rate_row.company_rate / 100)
                            ),
                        }
                    )
        elif row.mode != "CASH":
            coverage_plan = frappe.get_cached_value(
                "Healthcare Insurance Coverage Plan",
                {"coverage_plan_name": row.mode},
                "name",
            )
            for rate_row in insurance_rates:
                if (
                    rate_row.coverage_plan == coverage_plan
                    and rate_row.document_type == "Patient Appointment"
                ):
                    appointment_list.append(
                        {
                            "practitioner": row.practitioner,
                            "vc_technician": "",
                            "billing_item": row.billing_item,
                            "patient_count": row.patient_count,
                            "item_count": row.item_count,
                            "mode": row.mode,
                            "paid_amount": row.amount,
                            "vc_amount": flt(row.amount * flt(rate_row.vc_rate / 100)),
                            "company_amount": flt(
                                row.amount * flt(rate_row.company_rate / 100)
                            ),
                        }
                    )
    return appointment_list


def get_lab_commissions(
    filters, cash_rates, insurance_rates, excluded_services_map, vc_lab_users
):
    if filters.get("practitioner"):
        return []

    lab = dt("Lab Test")
    prescription = dt("Lab Prescription")
    case_wh = None
    if filters.get("vc_technician"):
        case_wh = lab.hms_tz_user_id == filters.get("vc_technician")
    else:
        case_wh = lab.hms_tz_user_id.isnotnull()

    lab_records = (
        frappe.qb.from_(lab)
        .inner_join(prescription)
        .on(
            lab.hms_tz_ref_childname == prescription.name
            and lab.ref_docname == prescription.parent
            and lab.template == prescription.lab_test_code
        )
        .select(
            lab.template,
            lab.hms_tz_submitted_by,
            lab.hms_tz_user_id,
            prescription.prescribe,
            Sum(prescription.amount).as_("amount"),
            Count(lab.patient).distinct().as_("patient_count"),
            Count(lab.template).as_("item_count"),
            Case()
            .when(prescription.prescribe == 0, lab.hms_tz_insurance_coverage_plan)
            .else_("CASH")
            .as_("mode"),
        )
        .where(
            (lab.ref_doctype == "Patient Encounter")
            & (lab.ref_docname == prescription.parent)
            & (lab.hms_tz_ref_childname == prescription.name)
            & (lab.docstatus == 1)
        )
        .where(
            (
                (lab.submitted_date >= filters.get("from_date"))
                & (lab.submitted_date <= filters.get("to_date"))
                & (lab.company == filters.get("company"))
                & (lab.workflow_state == "Lab Results Reviewed")
                & case_wh
            )
        )
        .groupby(
            Case()
            .when(prescription.prescribe == 0, lab.hms_tz_insurance_coverage_plan)
            .else_("CASH")
            .as_("mode"),
            lab.hms_tz_user_id,
            lab.template,
        )
    ).run(as_dict=1)

    lab_list = []
    excluded_lab_tests = excluded_services_map.get("Lab Test Template", [])
    lab_test_templates = [row.healthcare_service for row in excluded_lab_tests]

    for row in lab_records:
        if row.hms_tz_user_id not in vc_lab_users:
            continue

        if row.template in lab_test_templates:
            for excluded_lab_test in excluded_lab_tests:
                if row.template == excluded_lab_test.healthcare_service:
                    lab_list.append(
                        {
                            "practitioner": "",
                            "vc_technician": row.hms_tz_submitted_by,
                            "billing_item": row.template,
                            "patient_count": row.patient_count,
                            "item_count": row.item_count,
                            "mode": row.mode,
                            "paid_amount": row.amount,
                            "vc_amount": flt(
                                row.amount * flt(excluded_lab_test.vc_rate / 100)
                            ),
                            "company_amount": flt(
                                row.amount * flt(excluded_lab_test.company_rate / 100)
                            ),
                        }
                    )

        elif row.prescribe == 1 and row.mode == "CASH":
            for rate_row in cash_rates:
                if rate_row.document_type == "Lab Test":
                    lab_list.append(
                        {
                            "practitioner": "",
                            "vc_technician": row.hms_tz_submitted_by,
                            "billing_item": row.template,
                            "patient_count": row.patient_count,
                            "item_count": row.item_count,
                            "mode": row.mode,
                            "paid_amount": row.amount,
                            "vc_amount": flt(row.amount * flt(rate_row.vc_rate / 100)),
                            "company_amount": flt(
                                row.amount * flt(rate_row.company_rate / 100)
                            ),
                        }
                    )
        elif row.prescribe == 0 and row.mode != "CASH":
            coverage_plan_name = None
            if row.mode == "NH001~":
                coverage_plan_name = frappe.get_cached_value(
                    "Healthcare Insurance Coverage Plan",
                    {"name": row.mode},
                    "coverage_plan_name",
                )
            for rate_row in insurance_rates:
                if (
                    rate_row.coverage_plan == row.mode
                    and rate_row.document_type == "Lab Test"
                ):
                    lab_list.append(
                        {
                            "practitioner": "",
                            "vc_technician": row.hms_tz_submitted_by,
                            "billing_item": row.template,
                            "patient_count": row.patient_count,
                            "item_count": row.item_count,
                            "mode": (
                                coverage_plan_name if coverage_plan_name else row.mode
                            ),
                            "paid_amount": row.amount,
                            "vc_amount": flt(row.amount * flt(rate_row.vc_rate / 100)),
                            "company_amount": flt(
                                row.amount * flt(rate_row.company_rate / 100)
                            ),
                        }
                    )
    return lab_list
>>>>>>> a6711458 (feat: show cash and insurance vc rates for lab records)


def get_radiology_commissions(
    filters, cash_rates, insurance_rates, excluded_services_map, vc_radiology_users
):
    if filters.get("practitioner"):
        return []

    radiology = dt("Radiology Examination")
    prescription = dt("Radiology Procedure Prescription")
    case_wh = None
    if filters.get("vc_technician"):
        case_wh = radiology.hms_tz_user_id == filters.get("vc_technician")
    else:
        case_wh = radiology.hms_tz_user_id.isnotnull()

    radiology_records = (
        frappe.qb.from_(radiology)
        .inner_join(prescription)
        .on(
            radiology.hms_tz_ref_childname == prescription.name
            and radiology.ref_docname == prescription.parent
            and radiology.radiology_examination_template
            == prescription.radiology_examination_template
        )
        .select(
            radiology.radiology_examination_template,
            radiology.hms_tz_submitted_by,
            radiology.hms_tz_user_id,
            prescription.prescribe,
            Sum(prescription.amount).as_("amount"),
            Count(radiology.patient).distinct().as_("patient_count"),
            Count(radiology.radiology_examination_template).as_("item_count"),
            Case()
            .when(prescription.prescribe == 0, radiology.hms_tz_insurance_coverage_plan)
            .else_("CASH")
            .as_("mode"),
        )
        .where(
            (radiology.ref_doctype == "Patient Encounter")
            & (radiology.ref_docname == prescription.parent)
            & (radiology.hms_tz_ref_childname == prescription.name)
            & (radiology.docstatus == 1)
        )
        .where(
            (
                (radiology.hms_tz_submitted_date >= filters.get("from_date"))
                & (radiology.hms_tz_submitted_date <= filters.get("to_date"))
                & (radiology.company == filters.get("company"))
                & (radiology.workflow_state == "Submitted")
                & case_wh
            )
        )
        .groupby(
            Case()
            .when(prescription.prescribe == 0, radiology.hms_tz_insurance_coverage_plan)
            .else_("CASH")
            .as_("mode"),
            radiology.hms_tz_user_id,
            radiology.radiology_examination_template,
        )
    ).run(as_dict=1)

    radiology_list = []
    excluded_radiologies = excluded_services_map.get(
        "Radiology Examination Template", []
    )
    radiology_templates = [row.healthcare_service for row in excluded_radiologies]

    for row in radiology_records:
        if row.hms_tz_user_id not in vc_radiology_users:
            continue

        if row.radiology_examination_template in radiology_templates:
            for excluded_radiology in excluded_radiologies:
                if (
                    row.radiology_examination_template
                    == excluded_radiology.healthcare_service
                ):
                    radiology_list.append(
                        {
                            "practitioner": "",
                            "vc_technician": row.hms_tz_submitted_by,
                            "billing_item": row.radiology_examination_template,
                            "patient_count": row.patient_count,
                            "item_count": row.item_count,
                            "mode": row.mode,
                            "paid_amount": row.amount,
                            "vc_amount": flt(
                                row.amount * flt(excluded_radiology.vc_rate / 100)
                            ),
                            "company_amount": flt(
                                row.amount * flt(excluded_radiology.company_rate / 100)
                            ),
                        }
                    )

        elif row.prescribe == 1 and row.mode == "CASH":
            for rate_row in cash_rates:
                if rate_row.document_type == "Radiology Examination":
                    radiology_list.append(
                        {
                            "practitioner": "",
                            "vc_technician": row.hms_tz_submitted_by,
                            "billing_item": row.radiology_examination_template,
                            "patient_count": row.patient_count,
                            "item_count": row.item_count,
                            "mode": row.mode,
                            "paid_amount": row.amount,
                            "vc_amount": flt(row.amount * flt(rate_row.vc_rate / 100)),
                            "company_amount": flt(
                                row.amount * flt(rate_row.company_rate / 100)
                            ),
                        }
                    )
        elif row.prescribe == 0 and row.mode != "CASH":
            coverage_plan_name = None
            if row.mode == "NH001~":
                coverage_plan_name = frappe.get_cached_value(
                    "Healthcare Insurance Coverage Plan",
                    {"name": row.mode},
                    "coverage_plan_name",
                )
            for rate_row in insurance_rates:
                if (
                    rate_row.coverage_plan == row.mode
                    and rate_row.document_type == "Radiology Examination"
                ):
                    radiology_list.append(
                        {
                            "practitioner": "",
                            "vc_technician": row.hms_tz_submitted_by,
                            "billing_item": row.radiology_examination_template,
                            "patient_count": row.patient_count,
                            "item_count": row.item_count,
                            "mode": (
                                coverage_plan_name if coverage_plan_name else row.mode
                            ),
                            "paid_amount": row.amount,
                            "vc_amount": flt(row.amount * flt(rate_row.vc_rate / 100)),
                            "company_amount": flt(
                                row.amount * flt(rate_row.company_rate / 100)
                            ),
                        }
                    )
    return radiology_list


def get_procedure_commissions(
    filters, cash_rates, insurance_rates, excluded_services_map
):
    if filters.get("vc_technician"):
        return []

    procedure = dt("Clinical Procedure")
    prescription = dt("Procedure Prescription")
    case_wh = None
    if filters.get("practitioner"):
        case_wh = procedure.practitioner == filters.get("practitioner")
    else:
        case_wh = procedure.practitioner.isnotnull()

    procedure_records = (
        frappe.qb.from_(procedure)
        .inner_join(prescription)
        .on(
            procedure.hms_tz_ref_childname == prescription.name
            and procedure.ref_docname == prescription.parent
            and procedure.procedure_template == prescription.procedure
        )
        .select(
            procedure.procedure_template,
            procedure.practitioner,
            prescription.prescribe,
            Sum(prescription.amount).as_("amount"),
            Count(procedure.patient).distinct().as_("patient_count"),
            Count(procedure.procedure_template).as_("item_count"),
            Case()
            .when(prescription.prescribe == 0, procedure.hms_tz_insurance_coverage_plan)
            .else_("CASH")
            .as_("mode"),
        )
        .where(
            (procedure.ref_doctype == "Patient Encounter")
            & (procedure.ref_docname == prescription.parent)
            & (procedure.hms_tz_ref_childname == prescription.name)
            & (procedure.docstatus == 1)
        )
        .where(
            (
                (procedure.hms_tz_submitted_date >= filters.get("from_date"))
                & (procedure.hms_tz_submitted_date <= filters.get("to_date"))
                & (procedure.company == filters.get("company"))
                & (procedure.workflow_state == "Completed")
                & case_wh
            )
        )
        .groupby(
            Case()
            .when(prescription.prescribe == 0, procedure.hms_tz_insurance_coverage_plan)
            .else_("CASH")
            .as_("mode"),
            procedure.practitioner,
            procedure.procedure_template,
        )
    ).run(as_dict=1)

    procedure_list = []
    excluded_procedures = excluded_services_map.get("Clinical Procedure Template", [])
    excluded_procedure_templates = [
        row.healthcare_service for row in excluded_procedures
    ]

    for row in procedure_records:
        if row.procedure_template in excluded_procedure_templates:
            for excluded_procedure in excluded_procedures:
                if row.procedure_template == excluded_procedure.healthcare_service:
                    procedure_list.append(
                        {
                            "practitioner": row.practitioner,
                            "vc_technician": "",
                            "billing_item": row.procedure_template,
                            "patient_count": row.patient_count,
                            "item_count": row.item_count,
                            "mode": row.mode,
                            "paid_amount": row.amount,
                            "vc_amount": flt(
                                row.amount * flt(excluded_procedure.vc_rate / 100)
                            ),
                            "company_amount": flt(
                                row.amount * flt(excluded_procedure.company_rate / 100)
                            ),
                        }
                    )

        elif row.prescribe == 1 and row.mode == "CASH":
            for rate_row in cash_rates:
                if rate_row.document_type == "Clinical Procedure":
                    procedure_list.append(
                        {
                            "practitioner": row.practitioner,
                            "vc_technician": "",
                            "billing_item": row.procedure_template,
                            "patient_count": row.patient_count,
                            "item_count": row.item_count,
                            "mode": row.mode,
                            "paid_amount": row.amount,
                            "vc_amount": flt(row.amount * flt(rate_row.vc_rate / 100)),
                            "company_amount": flt(
                                row.amount * flt(rate_row.company_rate / 100)
                            ),
                        }
                    )
        elif row.prescribe == 0 and row.mode != "CASH":
            coverage_plan_name = None
            if row.mode == "NH001~":
                coverage_plan_name = frappe.get_cached_value(
                    "Healthcare Insurance Coverage Plan",
                    {"name": row.mode},
                    "coverage_plan_name",
                )
            for rate_row in insurance_rates:
                if (
                    rate_row.coverage_plan == row.mode
                    and rate_row.document_type == "Clinical Procedure"
                ):
                    procedure_list.append(
                        {
                            "practitioner": row.practitioner,
                            "vc_technician": "",
                            "billing_item": row.procedure_template,
                            "patient_count": row.patient_count,
                            "item_count": row.item_count,
                            "mode": (
                                coverage_plan_name if coverage_plan_name else row.mode
                            ),
                            "paid_amount": row.amount,
                            "vc_amount": flt(row.amount * flt(rate_row.vc_rate / 100)),
                            "company_amount": flt(
                                row.amount * flt(rate_row.company_rate / 100)
                            ),
                        }
                    )
    return procedure_list


def get_report_summary(args, summary_data):
    total_paid_amount = sum(
        [flt(row.get("paid_amount")) for row in summary_data if row.get("paid_amount")]
    )
    total_vc_amount = sum(
        [flt(row.get("vc_amount")) for row in summary_data if row.get("vc_amount")]
    )
    total_company_amount = sum(
        [
            flt(row.get("company_amount"))
            for row in summary_data
            if row.get("company_amount")
        ]
    )

    currency = frappe.get_cached_value("Company", args.company, "default_currency")
    return [
        {
            "value": total_paid_amount,
            "label": _("Total Paid Amount"),
            "datatype": "Currency",
            "currency": currency,
        },
        {
            "value": total_vc_amount,
            "label": _("Total VC Amount"),
            "datatype": "Currency",
            "currency": currency,
        },
        {
            "value": total_company_amount,
            "label": _("Total Company Amount"),
            "datatype": "Currency",
            "currency": currency,
        },
    ]
