# Copyright (c) 2023, Aakvatech and contributors
# For license information, please see license.txt

import frappe
from pypika import Case, functions as fn
from frappe.query_builder import DocType
from frappe.query_builder.functions import Sum, Count
from pypika.terms import ValueWrapper


def execute(filters=None):
    columns = get_columns(filters)

    if filters.get("show_only_cancelled_items") == 1:
        data = get_cancelled_data(filters)
        return columns, data

    else:
        if not filters.payment_mode:
            data = get_cash_insurance_data(filters)
            return columns, data

        elif filters.payment_mode == "Cash":
            data = get_cash_data(filters)
            return columns, data

        else:
            data = get_insurance_data(filters)
            return columns, data


def get_columns(filters):
    columns = [
        {"fieldname": "date", "label": "Date", "fieldtype": "Date", "width": 120},
        {
            "fieldname": "patient",
            "label": "Patient",
            "fieldtype": "Data",
            "width": 120,
        },
        {
            "fieldname": "patient_name",
            "label": "PatientName/CustomerName",
            "fieldtype": "Data",
            "width": 120,
        },
        {
            "fieldname": "patient_type",
            "label": "Patient Type",
            "fieldtype": "Data",
            "width": 120,
        },
        {
            "fieldname": "appointment_no",
            "label": "AppointmentNo",
            "fieldtype": "Data",
            "width": 120,
        },
    ]
    if not filters.show_only_cancelled_items:
        columns += [
            {
                "fieldname": "bill_no",
                "label": "Bill No",
                "fieldtype": "Data",
                "width": 120,
            },
            {
                "fieldname": "service_type",
                "label": "Service Type",
                "fieldtype": "Data",
                "width": 120,
            },
            {
                "fieldname": "service_name",
                "label": "Service Name",
                "fieldtype": "Data",
                "width": 120,
            },
            {"fieldname": "qty", "label": "Qty", "fieldtype": "Int", "width": 50},
            {
                "fieldname": "rate",
                "label": "Rate",
                "fieldtype": "Currency",
                "width": 120,
            },
            {
                "fieldname": "discount_amount",
                "label": "Discount Amount",
                "fieldtype": "Currency",
                "width": 120,
            },
            {
                "fieldname": "amount",
                "label": "Amount",
                "fieldtype": "Currency",
                "width": 120,
            },
            {
                "fieldname": "payment_method",
                "label": "Payment Method",
                "fieldtype": "Data",
                "width": 120,
            },
            {
                "fieldname": "department",
                "label": "Department",
                "fieldtype": "Data",
                "width": 120,
            },
            {
                "fieldnaeme": "practitioner",
                "label": "Practitioner",
                "fieldtype": "Data",
                "width": 120,
            },
            {
                "fieldname": "service_unit",
                "label": "Service Unit",
                "fieldtype": "Data",
                "width": 120,
            },
            {
                "fieldname": "status",
                "label": "Status",
                "fieldtype": "Data",
                "width": 120,
            },
            {
                "fieldname": "date_modified",
                "label": "Date Modified",
                "fieldtype": "Datetime",
                "width": 120,
            },
        ]

    elif filters.get("show_only_cancelled_items") == 1:
        columns += [
            {
                "fieldname": "encounter_no",
                "label": "Encounter No",
                "fieldtype": "Data",
                "width": 120,
            },
            {
                "fieldname": "bill_doctype",
                "label": "Bill Doctype",
                "fieldtype": "Data",
                "width": 120,
            },
            {
                "fieldname": "bill_no",
                "label": "Bill No",
                "fieldtype": "Data",
                "width": 120,
            },
            {
                "fieldname": "service_name",
                "label": "Service Name",
                "fieldtype": "Data",
                "width": 120,
            },
            {"fieldname": "qty", "label": "Qty", "fieldtype": "Int", "width": 50},
            {
                "fieldname": "rate",
                "label": "Rate",
                "fieldtype": "Currency",
                "width": 120,
            },
            {
                "fieldname": "amount",
                "label": "Amount",
                "fieldtype": "Currency",
                "width": 120,
            },
            {
                "fieldname": "payment_method",
                "label": "Payment Method",
                "fieldtype": "Data",
                "width": 120,
            },
            {
                "fieldname": "reference_no",
                "label": "LRPMT Return No",
                "fieldtype": "Data",
                "width": 120,
            },
            # {
            #     "fieldnaeme": "requested_by",
            #     "label": "Requested By",
            #     "fieldtype": "Data",
            #     "width": 120,
            # },
            # {
            #     "fieldname": "approved_by",
            #     "label": "Approved By",
            #     "fieldtype": "Data",
            #     "width": 120,
            # },
            {
                "fieldname": "reason",
                "label": "Cancellation Reason",
                "fieldtype": "Data",
                "width": 120,
            },
            {
                "fieldname": "date_modified",
                "label": "Date Modified",
                "fieldtype": "Datetime",
                "width": 120,
            },
        ]
    return columns


def get_cash_insurance_data(filters):
    cash_insurance_data = []
    cash_insurance_data += get_insurance_appointment_data(filters)
    cash_insurance_data += get_cash_appointment_data(filters)
    cash_insurance_data += get_insurance_lab_data(filters)
    cash_insurance_data += get_cash_lab_data(filters)
    cash_insurance_data += get_insurance_radiology_data(filters)
    cash_insurance_data += get_cash_radiology_data(filters)
    cash_insurance_data += get_insurance_procedure_data(filters)
    cash_insurance_data += get_cash_procedure_data(filters)
    cash_insurance_data += get_insurance_drug_data(filters)
    cash_insurance_data += get_cash_drug_data(filters)
    cash_insurance_data += get_direct_sales_drug_data(filters)
    cash_insurance_data += get_insurance_therapy_data(filters)
    cash_insurance_data += get_cash_therapy_data(filters)
    cash_insurance_data += get_insurance_ipd_beds_data(filters)
    cash_insurance_data += get_cash_ipd_beds_data(filters)
    cash_insurance_data += get_insurance_ipd_cons_data(filters)
    cash_insurance_data += get_cash_ipd_cons_data(filters)

    return cash_insurance_data


def get_cash_data(filters):
    cash_data = []
    cash_data += get_cash_appointment_data(filters)
    cash_data += get_cash_lab_data(filters)
    cash_data += get_cash_radiology_data(filters)
    cash_data += get_cash_procedure_data(filters)
    cash_data += get_cash_drug_data(filters)
    cash_data += get_direct_sales_drug_data(filters)
    cash_data += get_cash_therapy_data(filters)
    cash_data += get_cash_ipd_beds_data(filters)
    cash_data += get_cash_ipd_cons_data(filters)

    return cash_data


def get_insurance_data(filters):
    insurance_data = []
    insurance_data += get_insurance_appointment_data(filters)
    insurance_data += get_insurance_lab_data(filters)
    insurance_data += get_insurance_radiology_data(filters)
    insurance_data += get_insurance_procedure_data(filters)
    insurance_data += get_insurance_drug_data(filters)
    insurance_data += get_insurance_therapy_data(filters)
    insurance_data += get_insurance_ipd_beds_data(filters)
    insurance_data += get_insurance_ipd_cons_data(filters)

    return insurance_data


def get_insurance_appointment_data(filters):
    appointment = DocType("Patient Appointment")
    item = DocType("Item")

    insurance_appointment_query = (
        frappe.qb.from_(appointment)
        .inner_join(item)
        .on(appointment.billing_item == item.name)
        .select(
            appointment.appointment_date.as_("date"),
            appointment.name.as_("appointment_no"),
            appointment.name.as_("bill_no"),
            appointment.patient.as_("patient"),
            appointment.patient_name.as_("patient_name"),
            Case()
            .when(appointment.appointment_type.like("Emergency"), "In-Patient")
            .else_("Out-Patient")
            .as_("patient_type"),
            item.item_group.as_("service_type"),
            appointment.billing_item.as_("service_name"),
            appointment.coverage_plan_name.as_("payment_method"),
            Count("*").as_("qty"),
            fn.Max(appointment.paid_amount).as_("rate"),
            Sum(appointment.paid_amount).as_("amount"),
            Case()
            .when(appointment.status == "Closed", "Submitted")
            .else_("Draft")
            .as_("status"),
            appointment.practitioner.as_("practitioner"),
            appointment.department.as_("department"),
            appointment.service_unit.as_("service_unit"),
            appointment.modified.as_("date_modified"),
        )
        .where(
            (appointment.company == filters.company)
            & (appointment.appointment_date.between(filters.from_date, filters.to_date))
            & (appointment.status != "Cancelled")
            & (appointment.follow_up == 0)
            & (appointment.has_no_consultation_charges == 0)
            & (appointment.invoiced == 0)
            & (
                (appointment.insurance_subscription.isnotnull())
                & (appointment.insurance_subscription != "")
            )
        )
        .groupby(
            appointment.appointment_date,
            appointment.patient,
            appointment.name,
            appointment.billing_item,
            appointment.coverage_plan_name,
            appointment.practitioner,
            appointment.status,
        )
    )

    if filters.service_type:
        insurance_appointment_query = insurance_appointment_query.where(
            item.item_group == filters.service_type
        )

    if filters.payment_mode and filters.payment_mode != "Cash":
        insurance_appointment_query = insurance_appointment_query.where(
            appointment.insurance_company == filters.payment_mode
        )

    insurance_appointment_data = insurance_appointment_query.run(as_dict=True)

    return insurance_appointment_data


def get_cash_appointment_data(filters):
    appointment = DocType("Patient Appointment")
    item = DocType("Item")
    sii = DocType("Sales Invoice Item")

    cash_appointment_query = (
        frappe.qb.from_(appointment)
        .inner_join(item)
        .on(appointment.billing_item == item.name)
        .inner_join(sii)
        .on(appointment.name == sii.reference_dn)
        .select(
            appointment.appointment_date.as_("date"),
            appointment.name.as_("appointment_no"),
            appointment.name.as_("bill_no"),
            appointment.patient.as_("patient"),
            appointment.patient_name.as_("patient_name"),
            Case()
            .when(appointment.appointment_type.like("Emergency"), "In-Patient")
            .else_("Out-Patient")
            .as_("patient_type"),
            item.item_group.as_("service_type"),
            appointment.billing_item.as_("service_name"),
            ValueWrapper("Cash").as_("payment_method"),
            Count("*").as_("qty"),
            fn.Max(appointment.paid_amount).as_("rate"),
            Sum(sii.amount - sii.net_amount).as_("discount_amount"),
            Sum(sii.net_amount).as_("amount"),
            Case()
            .when(appointment.status == "Closed", "Submitted")
            .else_("Draft")
            .as_("status"),
            appointment.practitioner.as_("practitioner"),
            appointment.department.as_("department"),
            appointment.service_unit.as_("service_unit"),
            appointment.modified.as_("date_modified"),
        )
        .where(
            (appointment.company == filters.company)
            & (appointment.appointment_date.between(filters.from_date, filters.to_date))
            & (appointment.status != "Cancelled")
            & (appointment.follow_up == 0)
            & (appointment.has_no_consultation_charges == 0)
            & (appointment.invoiced == 1)
            & (
                (appointment.ref_sales_invoice.isnotnull())
                & (appointment.ref_sales_invoice != "")
            )
            & (sii.docstatus == 1)
            & ((sii.sales_invoice_item.isnull()) | (sii.sales_invoice_item == ""))
        )
        .groupby(
            appointment.appointment_date,
            appointment.patient,
            appointment.name,
            appointment.billing_item,
            appointment.ref_sales_invoice,
            appointment.practitioner,
            appointment.status,
        )
    )

    if filters.service_type:
        cash_appointment_query = cash_appointment_query.where(
            item.item_group == filters.service_type
        )

    cash_appointment_data = cash_appointment_query.run(as_dict=True)

    return cash_appointment_data


def get_insurance_lab_data(filters):
    lab = DocType("Lab Test")
    lab_prescription = DocType("Lab Prescription")
    template = DocType("Lab Test Template")
    encounter = DocType("Patient Encounter")

    insurance_lab_query = (
        frappe.qb.from_(lab)
        .inner_join(lab_prescription)
        .on(lab.hms_tz_ref_childname == lab_prescription.name)
        .inner_join(template)
        .on(lab.template == template.name)
        .inner_join(encounter)
        .on(lab.ref_docname == encounter.name)
        .select(
            lab.result_date.as_("date"),
            encounter.appointment.as_("appointment_no"),
            lab.name.as_("bill_no"),
            lab.patient.as_("patient"),
            lab.patient_name.as_("patient_name"),
            Case()
            .when(lab.inpatient_record.isnull(), "Out-Patient")
            .else_("In-Patient")
            .as_("patient_type"),
            template.lab_test_group.as_("service_type"),
            lab.template.as_("service_name"),
            lab.hms_tz_insurance_coverage_plan.as_("payment_method"),
            Count("*").as_("qty"),
            fn.Max(lab_prescription.amount).as_("rate"),
            Sum(lab_prescription.amount).as_("amount"),
            Case().when(lab.docstatus == 1, "Submitted").else_("Draft").as_("status"),
            lab.practitioner.as_("practitioner"),
            lab.department.as_("department"),
            lab_prescription.department_hsu.as_("service_unit"),
            lab.modified.as_("date_modified"),
        )
        .where(
            (lab.company == filters.company)
            & (lab.result_date.between(filters.from_date, filters.to_date))
            & ~lab.workflow_state.isin(["Not Serviced", "Submitted but Not Serviced"])
            & (
                (
                    lab.hms_tz_insurance_coverage_plan.isnotnull()
                    & (lab.hms_tz_insurance_coverage_plan != "")
                )
            )
            & (lab.docstatus != 2)
            & (lab.ref_doctype == "Patient Encounter")
            & (lab.ref_docname == lab_prescription.parent)
            & (lab.prescribe == 0)
            & (lab_prescription.prescribe == 0)
            & (lab_prescription.is_cancelled == 0)
            & (lab_prescription.is_not_available_inhouse == 0)
        )
        .groupby(
            lab.result_date,
            lab.patient,
            lab.name,
            lab.template,
            lab.hms_tz_insurance_coverage_plan,
            lab.practitioner,
            lab.docstatus,
        )
    )

    if filters.service_type:
        insurance_lab_query = insurance_lab_query.where(
            template.lab_test_group == filters.service_type
        )

    if filters.payment_mode and filters.payment_mode != "Cash":
        insurance_lab_query = insurance_lab_query.where(
            lab.insurance_company == filters.payment_mode
        )

    insurance_lab_data = insurance_lab_query.run(as_dict=True)

    return insurance_lab_data


def get_cash_lab_data(filters):
    lab = DocType("Lab Test")
    lab_prescription = DocType("Lab Prescription")
    template = DocType("Lab Test Template")
    sii = DocType("Sales Invoice Item")
    encounter = DocType("Patient Encounter")

    # Paid Lab Data for OPD Patients, Admitted and Discharged Patients
    # Link to Sales invoice
    paid_cash_lab_query = (
        frappe.qb.from_(lab)
        .inner_join(lab_prescription)
        .on(lab.hms_tz_ref_childname == lab_prescription.name)
        .inner_join(template)
        .on(lab.template == template.name)
        .inner_join(sii)
        .on(lab.hms_tz_ref_childname == sii.reference_dn)
        .inner_join(encounter)
        .on(lab.ref_docname == encounter.name)
        .select(
            lab.result_date.as_("date"),
            encounter.appointment.as_("appointment_no"),
            lab.name.as_("bill_no"),
            lab.patient.as_("patient"),
            lab.patient_name.as_("patient_name"),
            Case()
            .when(lab.inpatient_record.isnull(), "Out-Patient")
            .else_("In-Patient")
            .as_("patient_type"),
            template.lab_test_group.as_("service_type"),
            lab.template.as_("service_name"),
            ValueWrapper("Cash").as_("payment_method"),
            Count("*").as_("qty"),
            fn.Max(lab_prescription.amount).as_("rate"),
            Sum(sii.amount - sii.net_amount).as_("discount_amount"),
            Sum(sii.net_amount).as_("amount"),
            Case().when(lab.docstatus == 1, "Submitted").else_("Draft").as_("status"),
            lab.practitioner.as_("practitioner"),
            lab.department.as_("department"),
            lab_prescription.department_hsu.as_("service_unit"),
            lab.modified.as_("date_modified"),
        )
        .where(
            (lab.company == filters.company)
            & (lab.result_date.between(filters.from_date, filters.to_date))
            & (~lab.workflow_state.isin(["Not Serviced", "Submitted but Not Serviced"]))
            & (lab.docstatus != 2)
            & (lab.ref_doctype == "Patient Encounter")
            & (lab.ref_docname == lab_prescription.parent)
            & (lab.prescribe == 1)
            & (lab_prescription.prescribe == 1)
            & (lab_prescription.invoiced == 1)
            & (lab_prescription.is_cancelled == 0)
            & (lab_prescription.is_not_available_inhouse == 0)
            & (sii.docstatus == 1)
            & ((sii.sales_invoice_item.isnull()) | (sii.sales_invoice_item == ""))
        )
        .groupby(
            lab.result_date,
            lab.patient,
            lab.name,
            lab.template,
            lab.prescribe,
            lab.practitioner,
            lab.docstatus,
        )
    )

    if filters.service_type:
        paid_cash_lab_query = paid_cash_lab_query.where(
            template.lab_test_group == filters.service_type
        )

    paid_cash_lab_data = paid_cash_lab_query.run(as_dict=True)

    # Unpaid Lab Data for ongoing Admitted Patients
    # No link to Sales invoice
    unpaid_cash_lab_query = (
        frappe.qb.from_(lab)
        .inner_join(lab_prescription)
        .on(lab.hms_tz_ref_childname == lab_prescription.name)
        .inner_join(template)
        .on(lab.template == template.name)
        .inner_join(encounter)
        .on(lab.ref_docname == encounter.name)
        .select(
            lab.result_date.as_("date"),
            encounter.appointment.as_("appointment_no"),
            lab.name.as_("bill_no"),
            lab.patient.as_("patient"),
            lab.patient_name.as_("patient_name"),
            ValueWrapper("In-Patient").as_("patient_type"),
            template.lab_test_group.as_("service_type"),
            lab.template.as_("service_name"),
            ValueWrapper("Cash").as_("payment_method"),
            Count("*").as_("qty"),
            fn.Max(lab_prescription.amount).as_("rate"),
            Sum(lab_prescription.amount).as_("amount"),
            Case().when(lab.docstatus == 1, "Submitted").else_("Draft").as_("status"),
            lab.practitioner.as_("practitioner"),
            lab.department.as_("department"),
            lab_prescription.department_hsu.as_("service_unit"),
            lab.modified.as_("date_modified"),
        )
        .where(
            (lab.company == filters.company)
            & (lab.result_date.between(filters.from_date, filters.to_date))
            & (~lab.workflow_state.isin(["Not Serviced", "Submitted but Not Serviced"]))
            & (lab.docstatus != 2)
            & (lab.ref_doctype == "Patient Encounter")
            & (lab.ref_docname == lab_prescription.parent)
            & ((lab.inpatient_record.isnotnull()) & (lab.inpatient_record != ""))
            & (lab.prescribe == 1)
            & (lab_prescription.prescribe == 1)
            & (lab_prescription.invoiced == 0)
            & (lab_prescription.is_cancelled == 0)
            & (lab_prescription.is_not_available_inhouse == 0)
        )
        .groupby(
            lab.result_date,
            lab.patient,
            lab.name,
            lab.template,
            lab.prescribe,
            lab.practitioner,
            lab.docstatus,
        )
    )
    if filters.service_type:
        unpaid_cash_lab_query = unpaid_cash_lab_query.where(
            template.lab_test_group == filters.service_type
        )

    unpaid_cash_lab_data = unpaid_cash_lab_query.run(as_dict=True)

    return paid_cash_lab_data + unpaid_cash_lab_data


def get_insurance_radiology_data(filters):
    rad = DocType("Radiology Examination")
    rad_prescription = DocType("Radiology Procedure Prescription")
    template = DocType("Radiology Examination Template")
    encounter = DocType("Patient Encounter")

    insurance_rad_query = (
        frappe.qb.from_(rad)
        .inner_join(rad_prescription)
        .on(rad.hms_tz_ref_childname == rad_prescription.name)
        .inner_join(template)
        .on(rad.radiology_examination_template == template.name)
        .inner_join(encounter)
        .on(rad.ref_docname == encounter.name)
        .select(
            rad.start_date.as_("date"),
            encounter.appointment.as_("appointment_no"),
            rad.name.as_("bill_no"),
            rad.patient.as_("patient"),
            rad.patient_name.as_("patient_name"),
            Case()
            .when(rad.inpatient_record.isnull(), "Out-Patient")
            .else_("In-Patient")
            .as_("patient_type"),
            template.item_group.as_("service_type"),
            rad.radiology_examination_template.as_("service_name"),
            rad.hms_tz_insurance_coverage_plan.as_("payment_method"),
            Count("*").as_("qty"),
            fn.Max(rad_prescription.amount).as_("rate"),
            Sum(rad_prescription.amount).as_("amount"),
            Case().when(rad.docstatus == 1, "Submitted").else_("Draft").as_("status"),
            rad.practitioner.as_("practitioner"),
            rad.medical_department.as_("department"),
            rad_prescription.department_hsu.as_("service_unit"),
            rad.modified.as_("date_modified"),
        )
        .where(
            (rad.company == filters.company)
            & (rad.start_date.between(filters.from_date, filters.to_date))
            & (~rad.workflow_state.isin(["Not Serviced", "Submitted but Not Serviced"]))
            & (
                (rad.hms_tz_insurance_coverage_plan.isnotnull())
                & (rad.hms_tz_insurance_coverage_plan != "")
            )
            & (rad.docstatus != 2)
            & (rad.ref_doctype == "Patient Encounter")
            & (rad.ref_docname == rad_prescription.parent)
            & (rad.prescribe == 0)
            & (rad_prescription.prescribe == 0)
            & (rad_prescription.is_cancelled == 0)
            & (rad_prescription.is_not_available_inhouse == 0)
        )
        .groupby(
            rad.start_date,
            rad.patient,
            rad.name,
            rad.radiology_examination_template,
            rad.hms_tz_insurance_coverage_plan,
            rad.practitioner,
            rad.docstatus,
        )
    )

    if filters.service_type:
        insurance_rad_query = insurance_rad_query.where(
            template.item_group == filters.service_type
        )

    if filters.payment_mode and filters.payment_mode != "Cash":
        insurance_rad_query = insurance_rad_query.where(
            rad.insurance_company == filters.payment_mode
        )

    insurance_rad_data = insurance_rad_query.run(as_dict=True)

    return insurance_rad_data


def get_cash_radiology_data(filters):
    rad = DocType("Radiology Examination")
    rad_prescription = DocType("Radiology Procedure Prescription")
    template = DocType("Radiology Examination Template")
    sii = DocType("Sales Invoice Item")
    encounter = DocType("Patient Encounter")

    # Paid Radiology Data for OPD Patients, Admitted and Discharged Patients
    # Link to Sales invoice
    paid_cash_rad_query = (
        frappe.qb.from_(rad)
        .inner_join(rad_prescription)
        .on(rad.hms_tz_ref_childname == rad_prescription.name)
        .inner_join(template)
        .on(rad.radiology_examination_template == template.name)
        .inner_join(sii)
        .on(rad.hms_tz_ref_childname == sii.reference_dn)
        .inner_join(encounter)
        .on(rad.ref_docname == encounter.name)
        .select(
            rad.start_date.as_("date"),
            encounter.appointment.as_("appointment_no"),
            rad.name.as_("bill_no"),
            rad.patient.as_("patient"),
            rad.patient_name.as_("patient_name"),
            Case()
            .when(rad.inpatient_record.isnull(), "Out-Patient")
            .else_("In-Patient")
            .as_("patient_type"),
            template.item_group.as_("service_type"),
            rad.radiology_examination_template.as_("service_name"),
            ValueWrapper("Cash").as_("payment_method"),
            Count("*").as_("qty"),
            fn.Max(rad_prescription.amount).as_("rate"),
            Sum(sii.net_amount).as_("amount"),
            Sum(sii.amount - sii.net_amount).as_("discount_amount"),
            Case().when(rad.docstatus == 1, "Submitted").else_("Draft").as_("status"),
            rad.practitioner.as_("practitioner"),
            rad.medical_department.as_("department"),
            rad_prescription.department_hsu.as_("service_unit"),
            rad.modified.as_("date_modified"),
        )
        .where(
            (rad.company == filters.company)
            & (rad.start_date.between(filters.from_date, filters.to_date))
            & ~rad.workflow_state.isin(["Not Serviced", "Submitted but Not Serviced"])
            & (rad.docstatus != 2)
            & (rad.ref_doctype == "Patient Encounter")
            & (rad.ref_docname == rad_prescription.parent)
            & (rad.prescribe == 1)
            & (rad_prescription.invoiced == 1)
            & (rad_prescription.prescribe == 1)
            & (rad_prescription.is_cancelled == 0)
            & (rad_prescription.is_not_available_inhouse == 0)
            & (sii.docstatus == 1)
            & ((sii.sales_invoice_item.isnull()) | (sii.sales_invoice_item == ""))
        )
        .groupby(
            rad.start_date,
            rad.patient,
            rad.name,
            rad.radiology_examination_template,
            rad.hms_tz_insurance_coverage_plan,
            rad.practitioner,
            rad.docstatus,
        )
    )

    if filters.service_type:
        paid_cash_rad_query = paid_cash_rad_query.where(
            template.item_group == filters.service_type
        )

    paid_cash_rad_data = paid_cash_rad_query.run(as_dict=True)

    # Unpaid Radiology Data for ongoing Admitted Patients
    # No link to Sales invoice
    unpaid_cash_rad_query = (
        frappe.qb.from_(rad)
        .inner_join(rad_prescription)
        .on(rad.hms_tz_ref_childname == rad_prescription.name)
        .inner_join(template)
        .on(rad.radiology_examination_template == template.name)
        .inner_join(encounter)
        .on(rad.ref_docname == encounter.name)
        .select(
            rad.start_date.as_("date"),
            encounter.appointment.as_("appointment_no"),
            rad.name.as_("bill_no"),
            rad.patient.as_("patient"),
            rad.patient_name.as_("patient_name"),
            ValueWrapper("In-Patient").as_("patient_type"),
            template.item_group.as_("service_type"),
            rad.radiology_examination_template.as_("service_name"),
            ValueWrapper("Cash").as_("payment_method"),
            Count("*").as_("qty"),
            fn.Max(rad_prescription.amount).as_("rate"),
            Sum(rad_prescription.amount).as_("amount"),
            Case().when(rad.docstatus == 1, "Submitted").else_("Draft").as_("status"),
            rad.practitioner.as_("practitioner"),
            rad.medical_department.as_("department"),
            rad_prescription.department_hsu.as_("service_unit"),
            rad.modified.as_("date_modified"),
        )
        .where(
            (rad.company == filters.company)
            & (rad.start_date.between(filters.from_date, filters.to_date))
            & (~rad.workflow_state.isin(["Not Serviced", "Submitted but Not Serviced"]))
            & (rad.docstatus != 2)
            & (rad.ref_doctype == "Patient Encounter")
            & (rad.ref_docname == rad_prescription.parent)
            & ((rad.inpatient_record.isnotnull()) & (rad.inpatient_record != ""))
            & (rad.prescribe == 1)
            & (rad_prescription.prescribe == 1)
            & (rad_prescription.invoiced == 0)
            & (rad_prescription.is_cancelled == 0)
            & (rad_prescription.is_not_available_inhouse == 0)
        )
        .groupby(
            rad.start_date,
            rad.patient,
            rad.name,
            rad.radiology_examination_template,
            rad.hms_tz_insurance_coverage_plan,
            rad.practitioner,
            rad.docstatus,
        )
    )

    if filters.service_type:
        unpaid_cash_rad_query = unpaid_cash_rad_query.where(
            template.item_group == filters.service_type
        )

    unpaid_cash_rad_data = unpaid_cash_rad_query.run(as_dict=True)

    return paid_cash_rad_data + unpaid_cash_rad_data


def get_insurance_procedure_data(filters):
    procedure = DocType("Clinical Procedure")
    pp = DocType("Procedure Prescription")
    template = DocType("Clinical Procedure Template")
    encounter = DocType("Patient Encounter")

    insurance_procedure_query = (
        frappe.qb.from_(procedure)
        .inner_join(pp)
        .on(procedure.hms_tz_ref_childname == pp.name)
        .inner_join(template)
        .on(procedure.procedure_template == template.name)
        .inner_join(encounter)
        .on(procedure.ref_docname == encounter.name)
        .select(
            procedure.start_date.as_("date"),
            encounter.appointment.as_("appointment_no"),
            procedure.name.as_("bill_no"),
            procedure.patient.as_("patient"),
            procedure.patient_name.as_("patient_name"),
            Case()
            .when(procedure.inpatient_record.isnull(), "Out-Patient")
            .else_("In-Patient")
            .as_("patient_type"),
            template.item_group.as_("service_type"),
            procedure.procedure_template.as_("service_name"),
            procedure.hms_tz_insurance_coverage_plan.as_("payment_method"),
            Count("*").as_("qty"),
            fn.Max(pp.amount).as_("rate"),
            Sum(pp.amount).as_("amount"),
            Case()
            .when(procedure.docstatus == 1, "Submitted")
            .else_("Draft")
            .as_("status"),
            procedure.practitioner.as_("practitioner"),
            procedure.medical_department.as_("department"),
            pp.department_hsu.as_("service_unit"),
            procedure.modified.as_("date_modified"),
        )
        .where(
            (procedure.company == filters.company)
            & (procedure.start_date.between(filters.from_date, filters.to_date))
            & (
                ~procedure.workflow_state.isin(
                    ["Not Serviced", "Submitted but Not Serviced"]
                )
            )
            & (
                (procedure.hms_tz_insurance_coverage_plan.isnotnull())
                & (procedure.hms_tz_insurance_coverage_plan != "")
            )
            & (procedure.docstatus != 2)
            & (procedure.ref_doctype == "Patient Encounter")
            & (procedure.ref_docname == pp.parent)
            & (pp.prescribe == 0)
            & (pp.is_cancelled == 0)
            & (pp.is_not_available_inhouse == 0)
            & (procedure.prescribe == 0)
        )
        .groupby(
            procedure.start_date,
            procedure.patient,
            procedure.name,
            procedure.procedure_template,
            procedure.hms_tz_insurance_coverage_plan,
            procedure.practitioner,
            procedure.docstatus,
        )
    )

    if filters.service_type:
        insurance_procedure_query = insurance_procedure_query.where(
            template.item_group == filters.service_type
        )

    if filters.payment_mode and filters.payment_mode != "Cash":
        insurance_procedure_query = insurance_procedure_query.where(
            procedure.insurance_company == filters.payment_mode
        )

    insurance_procedure_data = insurance_procedure_query.run(as_dict=True)

    return insurance_procedure_data


def get_cash_procedure_data(filters):
    procedure = DocType("Clinical Procedure")
    pp = DocType("Procedure Prescription")
    template = DocType("Clinical Procedure Template")
    sii = DocType("Sales Invoice Item")
    encounter = DocType("Patient Encounter")

    # Paid Procedure Data for OPD Patients, Admitted and Discharged Patients
    # Link to Sales invoice
    paid_procedure_query = (
        frappe.qb.from_(procedure)
        .inner_join(pp)
        .on(procedure.hms_tz_ref_childname == pp.name)
        .inner_join(template)
        .on(procedure.procedure_template == template.name)
        .inner_join(sii)
        .on(procedure.hms_tz_ref_childname == sii.reference_dn)
        .inner_join(encounter)
        .on(procedure.ref_docname == encounter.name)
        .select(
            procedure.start_date.as_("date"),
            encounter.appointment.as_("appointment_no"),
            procedure.name.as_("bill_no"),
            procedure.patient.as_("patient"),
            procedure.patient_name.as_("patient_name"),
            Case()
            .when(procedure.inpatient_record.isnull(), "Out-Patient")
            .else_("In-Patient")
            .as_("patient_type"),
            template.item_group.as_("service_type"),
            procedure.procedure_template.as_("service_name"),
            ValueWrapper("Cash").as_("payment_method"),
            Count("*").as_("qty"),
            fn.Max(pp.amount).as_("rate"),
            Sum(sii.amount - sii.net_amount).as_("discount_amount"),
            Sum(sii.net_amount).as_("amount"),
            Case()
            .when(procedure.docstatus == 1, "Submitted")
            .else_("Draft")
            .as_("status"),
            procedure.practitioner.as_("practitioner"),
            procedure.medical_department.as_("department"),
            pp.department_hsu.as_("service_unit"),
            procedure.modified.as_("date_modified"),
        )
        .where(
            (procedure.company == filters.company)
            & (procedure.start_date.between(filters.from_date, filters.to_date))
            & (
                ~procedure.workflow_state.isin(
                    ["Not Serviced", "Submitted but Not Serviced"]
                )
            )
            & (procedure.docstatus != 2)
            & (procedure.ref_doctype == "Patient Encounter")
            & (procedure.ref_docname.isnotnull())
            & (procedure.ref_docname == pp.parent)
            & (pp.invoiced == 1)
            & (procedure.prescribe == 1)
            & (pp.prescribe == 1)
            & (pp.is_cancelled == 0)
            & (pp.is_not_available_inhouse == 0)
            & (sii.docstatus == 1)
            & ((sii.sales_invoice_item.isnull()) | (sii.sales_invoice_item == ""))
        )
        .groupby(
            procedure.start_date,
            procedure.patient,
            procedure.name,
            procedure.procedure_template,
            procedure.prescribe,
            procedure.practitioner,
            procedure.docstatus,
        )
    )

    if filters.service_type:
        paid_procedure_query = paid_procedure_query.where(
            template.item_group == filters.service_type
        )
    paid_procedure_data = paid_procedure_query.run(as_dict=True)

    # Unpaid Radiology Data for ongoing Admitted Patients
    # No link to Sales invoice
    unpaid_procedure_query = (
        frappe.qb.from_(procedure)
        .inner_join(pp)
        .on(procedure.hms_tz_ref_childname == pp.name)
        .inner_join(template)
        .on(procedure.procedure_template == template.name)
        .inner_join(encounter)
        .on(procedure.ref_docname == encounter.name)
        .select(
            procedure.start_date.as_("date"),
            encounter.appointment.as_("appointment_no"),
            procedure.name.as_("bill_no"),
            procedure.patient.as_("patient"),
            procedure.patient_name.as_("patient_name"),
            ValueWrapper("In-Patient").as_("patient_type"),
            template.item_group.as_("service_type"),
            procedure.procedure_template.as_("service_name"),
            ValueWrapper("Cash").as_("payment_method"),
            Count("*").as_("qty"),
            fn.Max(pp.amount).as_("rate"),
            Sum(pp.amount).as_("amount"),
            Case()
            .when(procedure.docstatus == 1, "Submitted")
            .else_("Draft")
            .as_("status"),
            procedure.practitioner.as_("practitioner"),
            procedure.medical_department.as_("department"),
            pp.department_hsu.as_("service_unit"),
            procedure.modified.as_("date_modified"),
        )
        .where(
            (procedure.company == filters.company)
            & (procedure.start_date.between(filters.from_date, filters.to_date))
            & (
                ~procedure.workflow_state.isin(
                    ["Not Serviced", "Submitted but Not Serviced"]
                )
            )
            & (procedure.docstatus != 2)
            & (procedure.ref_doctype == "Patient Encounter")
            & (procedure.ref_docname.isnotnull())
            & (procedure.ref_docname == pp.parent)
            & (
                (procedure.inpatient_record.isnotnull())
                & (procedure.inpatient_record != "")
            )
            & (procedure.prescribe == 1)
            & (pp.prescribe == 1)
            & (pp.invoiced == 0)
            & (pp.is_cancelled == 0)
            & (pp.is_not_available_inhouse == 0)
        )
        .groupby(
            procedure.start_date,
            procedure.patient,
            procedure.name,
            procedure.procedure_template,
            procedure.prescribe,
            procedure.practitioner,
            procedure.docstatus,
        )
    )

    if filters.service_type:
        unpaid_procedure_query = unpaid_procedure_query.where(
            template.item_group == filters.service_type
        )
    unpaid_procedure_data = unpaid_procedure_query.run(as_dict=True)

    return paid_procedure_data + unpaid_procedure_data


def get_insurance_drug_data(filters):
    pe = DocType("Patient Encounter")
    dp = DocType("Drug Prescription")
    dn = DocType("Delivery Note")
    md = DocType("Medication")

    insurance_drug_query = (
        frappe.qb.from_(pe)
        .inner_join(dp)
        .on(dp.parent == pe.name)
        .inner_join(md)
        .on(dp.drug_code == md.name)
        .inner_join(dn)
        .on(pe.name == dn.reference_name)
        .select(
            pe.encounter_date.as_("date"),
            pe.appointment.as_("appointment_no"),
            dn.name.as_("bill_no"),
            pe.patient.as_("patient"),
            pe.patient_name.as_("patient_name"),
            Case()
            .when(pe.inpatient_record.isnull(), "Out-Patient")
            .else_("In-Patient")
            .as_("patient_type"),
            md.item_group.as_("service_type"),
            dp.drug_code.as_("service_name"),
            dn.coverage_plan_name.as_("payment_method"),
            Sum(dp.quantity - dp.quantity_returned).as_("qty"),
            fn.Max(dp.amount).as_("rate"),
            Sum((dp.quantity - dp.quantity_returned) * dp.amount).as_("amount"),
            Case().when(dn.docstatus == 1, "Submitted").else_("Draft").as_("status"),
            pe.practitioner.as_("practitioner"),
            md.healthcare_service_order_category.as_("department"),
            pe.healthcare_service_unit.as_("service_unit"),
            dn.modified.as_("date_modified"),
        )
        .where(
            (pe.company == filters.company)
            & (pe.encounter_date.between(filters.from_date, filters.to_date))
            & (dp.prescribe == 0)
            & (dp.is_cancelled == 0)
            & (dp.is_not_available_inhouse == 0)
            & (dn.docstatus != 2)
            & (dn.is_return == 0)
            & (~dn.workflow_state.isin(["Not Serviced", "Is Return"]))
            & ((dn.coverage_plan_name.isnotnull()) & (dn.coverage_plan_name != ""))
        )
        .groupby(
            pe.encounter_date,
            pe.patient,
            dn.name,
            dp.drug_code,
            pe.insurance_coverage_plan,
            pe.practitioner,
            dn.docstatus,
        )
    )
    if filters.service_type:
        insurance_drug_query = insurance_drug_query.where(
            md.item_group == filters.service_type
        )

    if filters.payment_mode and filters.payment_mode != "Cash":
        insurance_drug_query = insurance_drug_query.where(
            pe.insurance_company == filters.payment_mode
        )

    insurance_drug_data = insurance_drug_query.run(as_dict=True)

    return insurance_drug_data


def get_cash_drug_data(filters):
    pe = DocType("Patient Encounter")
    dp = DocType("Drug Prescription")
    dn = DocType("Delivery Note")
    md = DocType("Medication")
    sii = DocType("Sales Invoice Item")

    # Paid Drug Data for OPD Patients, Admitted and Discharged Patients
    # Link to Sales invoice
    paid_drug_query = (
        frappe.qb.from_(pe)
        .inner_join(dp)
        .on(dp.parent == pe.name)
        .inner_join(md)
        .on(dp.drug_code == md.name)
        .inner_join(sii)
        .on(dp.name == sii.reference_dn)
        .inner_join(dn)
        .on(pe.name == dn.reference_name)
        .select(
            pe.encounter_date.as_("date"),
            pe.appointment.as_("appointment_no"),
            dn.name.as_("bill_no"),
            pe.patient.as_("patient"),
            pe.patient_name.as_("patient_name"),
            Case()
            .when(pe.inpatient_record.isnull(), "Out-Patient")
            .else_("In-Patient")
            .as_("patient_type"),
            md.item_group.as_("service_type"),
            dp.drug_code.as_("service_name"),
            ValueWrapper("Cash").as_("payment_method"),
            Sum(dp.quantity - dp.quantity_returned).as_("qty"),
            fn.Max(dp.amount).as_("rate"),
            Sum(
                ((dp.quantity - dp.quantity_returned) * dp.amount) - sii.net_amount
            ).as_("discount_amount"),
            Sum((dp.quantity - dp.quantity_returned) * sii.net_rate).as_("amount"),
            Case().when(dn.docstatus == 1, "Submitted").else_("Draft").as_("status"),
            pe.practitioner.as_("practitioner"),
            md.healthcare_service_order_category.as_("department"),
            pe.healthcare_service_unit.as_("service_unit"),
            dn.modified.as_("date_modified"),
        )
        .where(
            (pe.company == filters.company)
            & (pe.encounter_date.between(filters.from_date, filters.to_date))
            & (dp.prescribe == 1)
            & (dp.invoiced == 1)
            & (dp.is_cancelled == 0)
            & (dp.is_not_available_inhouse == 0)
            & (~dn.workflow_state.isin(["Not Serviced", "Is Return"]))
            & ((dn.coverage_plan_name.isnull()) | (dn.coverage_plan_name == ""))
            & (dn.docstatus != 2)
            & (dn.is_return == 0)
            & (sii.docstatus == 1)
            & ((sii.sales_invoice_item.isnull()) | (sii.sales_invoice_item == ""))
        )
        .groupby(
            pe.encounter_date,
            pe.patient,
            dn.name,
            dp.drug_code,
            ValueWrapper("Cash").as_("payment_method"),
            pe.practitioner,
            dn.docstatus,
        )
    )
    if filters.service_type:
        paid_drug_query = paid_drug_query.where(md.item_group == filters.service_type)

    paid_drug_data = paid_drug_query.run(as_dict=True)

    # Unpaid Drug Data for ongoing Admitted Patients
    # No link to Sales invoice
    unpaid_drug_query = (
        frappe.qb.from_(pe)
        .inner_join(dp)
        .on(dp.parent == pe.name)
        .inner_join(md)
        .on(dp.drug_code == md.name)
        .inner_join(dn)
        .on(pe.name == dn.reference_name)
        .select(
            pe.encounter_date.as_("date"),
            pe.appointment.as_("appointment_no"),
            dn.name.as_("bill_no"),
            pe.patient.as_("patient"),
            pe.patient_name.as_("patient_name"),
            ValueWrapper("In-Patient").as_("patient_type"),
            md.item_group.as_("service_type"),
            dp.drug_code.as_("service_name"),
            ValueWrapper("Cash").as_("payment_method"),
            Sum(dp.quantity - dp.quantity_returned).as_("qty"),
            fn.Max(dp.amount).as_("rate"),
            Sum((dp.quantity - dp.quantity_returned) * dp.amount).as_("amount"),
            Case().when(dn.docstatus == 1, "Submitted").else_("Draft").as_("status"),
            pe.practitioner.as_("practitioner"),
            md.healthcare_service_order_category.as_("department"),
            pe.healthcare_service_unit.as_("service_unit"),
            dn.modified.as_("date_modified"),
        )
        .where(
            (pe.company == filters.company)
            & (pe.encounter_date.between(filters.from_date, filters.to_date))
            & ((pe.inpatient_record.isnotnull()) & (pe.inpatient_record != ""))
            & (dp.prescribe == 1)
            & (dp.invoiced == 0)
            & (dp.is_cancelled == 0)
            & (dp.is_not_available_inhouse == 0)
            & (~dn.workflow_state.isin(["Not Serviced", "Is Return"]))
            & ((dn.coverage_plan_name.isnull()) | (dn.coverage_plan_name == ""))
            & (dn.docstatus != 2)
            & (dn.is_return == 0)
        )
        .groupby(
            pe.encounter_date,
            pe.patient,
            dn.name,
            dp.drug_code,
            ValueWrapper("Cash").as_("payment_method"),
            pe.practitioner,
            dn.docstatus,
        )
    )
    if filters.service_type:
        unpaid_drug_query = unpaid_drug_query.where(
            md.item_group == filters.service_type
        )

    unpaid_drug_data = unpaid_drug_query.run(as_dict=True)

    return paid_drug_data + unpaid_drug_data


def get_direct_sales_drug_data(filters):
    dn = DocType("Delivery Note")
    dni = DocType("Delivery Note Item")

    direct_sales_drug_query = (
        frappe.qb.from_(dn)
        .inner_join(dni)
        .on(dn.name == dni.parent)
        .select(
            dn.posting_date.as_("date"),
            dn.name.as_("bill_no"),
            ValueWrapper("Outsider Customer").as_("patient"),
            dn.customer_name.as_("patient_name"),
            ValueWrapper("Out-Patient").as_("patient_type"),
            dni.item_group.as_("service_type"),
            dni.item_code.as_("service_name"),
            ValueWrapper("Cash").as_("payment_method"),
            Sum(dni.qty).as_("qty"),
            fn.Max(dni.net_rate).as_("rate"),
            Sum(dni.net_amount).as_("amount"),
            Sum(dni.amount - dni.net_amount).as_("discount_amount"),
            Case().when(dn.docstatus == 1, "Submitted").else_("Draft").as_("status"),
            dni.healthcare_practitioner.as_("practitioner"),
            ValueWrapper("Pharmacy").as_("department"),
            dni.healthcare_service_unit.as_("service_unit"),
            dn.modified.as_("date_modified"),
        )
        .where(
            (dn.company == filters.company)
            & (dn.posting_date.between(filters.from_date, filters.to_date))
            & (~dn.workflow_state.isin(["Not Serviced", "Is Return"]))
            & (dn.docstatus != 2)
            & (dn.is_return == 0)
            & (dn.patient.isnull() | (dn.patient == ""))
            & ((dn.form_sales_invoice.isnotnull()) & (dn.form_sales_invoice != ""))
        )
        .groupby(
            dn.posting_date,
            dn.customer_name,
            dn.name,
            dni.item_code,
            dn.form_sales_invoice,
            dni.healthcare_practitioner,
            dn.docstatus,
        )
    )
    if filters.service_type:
        direct_sales_drug_query = direct_sales_drug_query.where(
            dni.item_group == filters.service_type
        )
    direct_sales_drug_data = direct_sales_drug_query.run(as_dict=True)

    return direct_sales_drug_data


def get_insurance_therapy_data(filters):
    tp = DocType("Therapy Plan")
    tpd = DocType("Therapy Plan Detail")
    tt = DocType("Therapy Type")
    pe = DocType("Patient Encounter")

    insurance_therapy_query = (
        frappe.qb.from_(tp)
        .inner_join(pe)
        .on(tp.ref_docname == pe.name)
        .inner_join(tpd)
        .on(pe.name == tpd.parent)
        .inner_join(tt)
        .on(tpd.therapy_type == tt.name)
        .select(
            tp.start_date.as_("date"),
            tp.hms_tz_appointment.as_("appointment_no"),
            tp.name.as_("bill_no"),
            tp.patient.as_("patient"),
            tp.patient_name.as_("patient_name"),
            Case()
            .when(pe.inpatient_record.isnull(), "Out-Patient")
            .else_("In-Patient")
            .as_("patient_type"),
            tt.item_group.as_("service_type"),
            tpd.therapy_type.as_("service_name"),
            tp.hms_tz_insurance_coverage_plan.as_("payment_method"),
            Count("*").as_("qty"),
            fn.Max(tpd.amount).as_("rate"),
            Sum(tpd.amount).as_("amount"),
            Case()
            .when(tp.status == "Completed", "Submitted")
            .else_("Draft")
            .as_("status"),
            pe.practitioner.as_("practitioner"),
            tt.medical_department.as_("department"),
            tpd.department_hsu.as_("service_unit"),
            tp.modified.as_("date_modified"),
        )
        .where(
            (tp.company == filters.company)
            & (tp.start_date.between(filters.from_date, filters.to_date))
            & (tpd.is_cancelled == 0)
            & (tpd.is_not_available_inhouse == 0)
            & (tpd.invoiced == 0)
            & (
                (tp.hms_tz_insurance_coverage_plan.isnotnull())
                & (tp.hms_tz_insurance_coverage_plan != "")
            )
        )
        .groupby(
            tp.start_date,
            tp.patient,
            tp.name,
            tpd.therapy_type,
            tp.hms_tz_insurance_coverage_plan,
            pe.practitioner,
            tp.status,
        )
    )

    if filters.service_type:
        insurance_therapy_query = insurance_therapy_query.where(
            tt.item_group == filters.service_type
        )

    if filters.payment_mode and filters.payment_mode != "Cash":
        insurance_therapy_query = insurance_therapy_query.where(
            pe.insurance_company == filters.payment_mode
        )

    insurance_therapy_data = insurance_therapy_query.run(as_dict=True)

    return insurance_therapy_data


def get_cash_therapy_data(filters):
    tp = DocType("Therapy Plan")
    tpd = DocType("Therapy Plan Detail")
    tt = DocType("Therapy Type")
    sii = DocType("Sales Invoice Item")
    pe = DocType("Patient Encounter")

    # Paid Therapy Data for OPD Patients, Admitted and Discharged Patients
    # Link to Sales invoice
    paid_therapy_query = (
        frappe.qb.from_(tp)
        .inner_join(pe)
        .on(tp.ref_docname == pe.name)
        .inner_join(tpd)
        .on(pe.name == tpd.parent)
        .inner_join(tt)
        .on(tpd.therapy_type == tt.name)
        .inner_join(sii)
        .on(tpd.name == sii.reference_dn)
        .select(
            tp.start_date.as_("date"),
            tp.hms_tz_appointment.as_("appointment_no"),
            tp.name.as_("bill_no"),
            tp.patient.as_("patient"),
            tp.patient_name.as_("patient_name"),
            Case()
            .when(pe.inpatient_record.isnull(), "Out-Patient")
            .else_("In-Patient")
            .as_("patient_type"),
            tt.item_group.as_("service_type"),
            tpd.therapy_type.as_("service_name"),
            ValueWrapper("Cash").as_("payment_method"),
            Count("*").as_("qty"),
            fn.Max(tpd.amount).as_("rate"),
            (sii.amount - sii.net_amount).as_("discount_amount"),
            Sum(sii.net_amount).as_("amount"),
            Case()
            .when(tp.status == "Completed", "Submitted")
            .else_("Draft")
            .as_("status"),
            pe.practitioner.as_("practitioner"),
            tt.medical_department.as_("department"),
            tpd.department_hsu.as_("service_unit"),
            tp.modified.as_("date_modified"),
        )
        .where(
            (tp.company == filters.company)
            & (tp.start_date.between(filters.from_date, filters.to_date))
            & (tpd.prescribe == 1)
            & (tpd.is_cancelled == 0)
            & (tpd.is_not_available_inhouse == 0)
            & (tpd.invoiced == 1)
            & (sii.docstatus == 1)
            & ((sii.sales_invoice_item.isnull()) | (sii.sales_invoice_item == ""))
        )
        .groupby(
            tp.start_date,
            tp.patient,
            tp.name,
            tpd.therapy_type,
            ValueWrapper("Cash").as_("payment_method"),
            pe.practitioner,
            tp.status,
        )
    )

    if filters.service_type:
        paid_therapy_query = paid_therapy_query.where(
            tt.item_group == filters.service_type
        )

    paid_therapy_data = paid_therapy_query.run(as_dict=True)

    # Unpaid Therapy Data for ongoing Admitted Patients
    # No link to Sales invoice
    unpaid_therapy_query = (
        frappe.qb.from_(tp)
        .inner_join(pe)
        .on(tp.ref_docname == pe.name)
        .inner_join(tpd)
        .on(pe.name == tpd.parent)
        .inner_join(tt)
        .on(tpd.therapy_type == tt.name)
        .select(
            tp.start_date.as_("date"),
            tp.hms_tz_appointment.as_("appointment_no"),
            tp.name.as_("bill_no"),
            tp.patient.as_("patient"),
            tp.patient_name.as_("patient_name"),
            Case()
            .when(pe.inpatient_record.isnull(), "Out-Patient")
            .else_("In-Patient")
            .as_("patient_type"),
            tt.item_group.as_("service_type"),
            tpd.therapy_type.as_("service_name"),
            ValueWrapper("Cash").as_("payment_method"),
            Count("*").as_("qty"),
            fn.Max(tpd.amount).as_("rate"),
            Sum(tpd.amount).as_("amount"),
            Case()
            .when(tp.status == "Completed", "Submitted")
            .else_("Draft")
            .as_("status"),
            pe.practitioner.as_("practitioner"),
            tt.medical_department.as_("department"),
            tpd.department_hsu.as_("service_unit"),
            tp.modified.as_("date_modified"),
        )
        .where(
            (tp.company == filters.company)
            & (tp.start_date.between(filters.from_date, filters.to_date))
            & (tpd.prescribe == 1)
            & (tpd.is_cancelled == 0)
            & (tpd.is_not_available_inhouse == 0)
            & (tpd.invoiced == 0)
            & ((pe.inpatient_record.isnotnull()) & (pe.inpatient_record != ""))
        )
        .groupby(
            tp.start_date,
            tp.patient,
            tp.name,
            tpd.therapy_type,
            ValueWrapper("Cash").as_("payment_method"),
            pe.practitioner,
            tp.status,
        )
    )

    if filters.service_type:
        unpaid_therapy_query = unpaid_therapy_query.where(
            tt.item_group == filters.service_type
        )

    unpaid_therapy_data = unpaid_therapy_query.run(as_dict=True)

    return paid_therapy_data + unpaid_therapy_data


def get_insurance_ipd_beds_data(filters):
    io = DocType("Inpatient Occupancy")
    ip = DocType("Inpatient Record")
    hsu = DocType("Healthcare Service Unit")
    hsut = DocType("Healthcare Service Unit Type")

    insurance_ipd_beds_query = (
        frappe.qb.from_(io)
        .inner_join(ip)
        .on(io.parent == ip.name)
        .inner_join(hsu)
        .on(io.service_unit == hsu.name)
        .inner_join(hsut)
        .on(hsu.service_unit_type == hsut.name)
        .select(
            fn.Date(io.check_in).as_("date"),
            ip.patient_appointment.as_("appointment_no"),
            ip.name.as_("bill_no"),
            ip.patient.as_("patient"),
            ip.patient_name.as_("patient_name"),
            ValueWrapper("In-Patient").as_("patient_type"),
            hsut.item_group.as_("service_type"),
            hsu.service_unit_type.as_("service_name"),
            ip.insurance_coverage_plan.as_("payment_method"),
            Count("*").as_("qty"),
            fn.Max(io.amount).as_("rate"),
            Sum(io.amount).as_("amount"),
            hsu.service_unit_type.as_("department"),
            hsu.parent_healthcare_service_unit.as_("service_unit"),
            io.modified.as_("date_modified"),
        )
        .where(
            (ip.company == filters.company)
            & (io.check_in.between(filters.from_date, filters.to_date))
            & (io.is_confirmed == 1)
            & (
                (ip.insurance_coverage_plan.isnotnull())
                & (ip.insurance_coverage_plan != "")
            )
        )
        .groupby(
            fn.Date(io.check_in),
            ip.patient,
            ip.name,
            io.name,
            hsu.service_unit_type,
            ip.insurance_coverage_plan,
        )
    )

    if filters.service_type:
        insurance_ipd_beds_query = insurance_ipd_beds_query.where(
            hsut.item_group == filters.service_type
        )

    if filters.payment_mode and filters.payment_mode != "Cash":
        insurance_ipd_beds_query = insurance_ipd_beds_query.where(
            ip.insurance_company == filters.payment_mode
        )

    insurance_ipd_beds_data = insurance_ipd_beds_query.run(as_dict=True)

    return insurance_ipd_beds_data


def get_cash_ipd_beds_data(filters):
    io = DocType("Inpatient Occupancy")
    ip = DocType("Inpatient Record")
    hsu = DocType("Healthcare Service Unit")
    hsut = DocType("Healthcare Service Unit Type")
    sii = DocType("Sales Invoice Item")

    cash_ipd_beds_query = (
        frappe.qb.from_(io)
        .inner_join(ip)
        .on(io.parent == ip.name)
        .inner_join(hsu)
        .on(io.service_unit == hsu.name)
        .inner_join(hsut)
        .on(hsu.service_unit_type == hsut.name)
        .inner_join(sii)
        .on(io.name == sii.reference_dn)
        .select(
            fn.Date(io.check_in).as_("date"),
            ip.patient_appointment.as_("appointment_no"),
            ip.name.as_("bill_no"),
            ip.patient.as_("patient"),
            ip.patient_name.as_("patient_name"),
            ValueWrapper("In-Patient").as_("patient_type"),
            hsut.item_group.as_("service_type"),
            hsu.service_unit_type.as_("service_name"),
            ValueWrapper("Cash").as_("payment_method"),
            Count("*").as_("qty"),
            fn.Max(io.amount).as_("rate"),
            Sum(sii.net_amount).as_("amount"),
            Sum(sii.amount - sii.net_amount).as_("discount_amount"),
            hsu.service_unit_type.as_("department"),
            hsu.parent_healthcare_service_unit.as_("service_unit"),
            io.modified.as_("date_modified"),
        )
        .where(
            (ip.company == filters.company)
            & (io.check_in.between(filters.from_date, filters.to_date))
            & (io.is_confirmed == 1)
            & (io.invoiced == 1)
            & (ip.insurance_coverage_plan.isnull() | (ip.insurance_coverage_plan == ""))
            & (sii.docstatus == 1)
            & ((sii.sales_invoice_item.isnull()) | (sii.sales_invoice_item == ""))
        )
        .groupby(
            fn.Date(io.check_in),
            ip.patient,
            ip.name,
            io.name,
            hsu.service_unit_type,
            ip.insurance_coverage_plan,
        )
    )
    if filters.service_type:
        cash_ipd_beds_query = cash_ipd_beds_query.where(
            hsut.item_group == filters.service_type
        )

    cash_ipd_beds_data = cash_ipd_beds_query.run(as_dict=True)

    return cash_ipd_beds_data


def get_insurance_ipd_cons_data(filters):
    ic = DocType("Inpatient Consultancy")
    ip = DocType("Inpatient Record")
    it = DocType("Item")
    pe = DocType("Patient Encounter")

    insurance_ipd_cons_query = (
        frappe.qb.from_(ic)
        .inner_join(ip)
        .on(ic.parent == ip.name)
        .inner_join(it)
        .on(ic.consultation_item == it.name)
        .inner_join(pe)
        .on(ic.encounter == pe.name)
        .select(
            ic.date.as_("date"),
            ip.patient_appointment.as_("appointment_no"),
            ip.name.as_("bill_no"),
            ip.patient.as_("patient"),
            ip.patient_name.as_("patient_name"),
            ValueWrapper("In-Patient").as_("patient_type"),
            it.item_group.as_("service_type"),
            ic.consultation_item.as_("service_name"),
            ip.insurance_coverage_plan.as_("payment_method"),
            Count("*").as_("qty"),
            fn.Max(ic.rate).as_("rate"),
            Sum(ic.rate).as_("amount"),
            pe.medical_department.as_("department"),
            ic.healthcare_practitioner.as_("practitioner"),
            pe.healthcare_service_unit.as_("service_unit"),
            ic.modified.as_("date_modified"),
        )
        .where(
            (ip.company == filters.company)
            & (ic.date.between(filters.from_date, filters.to_date))
            & (ic.is_confirmed == 1)
            & (
                (ip.insurance_coverage_plan.isnotnull())
                & (ip.insurance_coverage_plan != "")
            )
        )
        .groupby(
            ic.date,
            ip.patient,
            ip.name,
            ic.name,
            ic.consultation_item,
            ip.insurance_coverage_plan,
            ic.healthcare_practitioner,
        )
    )

    if filters.service_type:
        insurance_ipd_cons_query = insurance_ipd_cons_query.where(
            it.item_group == filters.service_type
        )

    if filters.payment_mode and filters.payment_mode != "Cash":
        insurance_ipd_cons_query = insurance_ipd_cons_query.where(
            ip.insurance_company == filters.payment_mode
        )

    insurance_ipd_cons_data = insurance_ipd_cons_query.run(as_dict=True)

    return insurance_ipd_cons_data


def get_cash_ipd_cons_data(filters):
    ic = DocType("Inpatient Consultancy")
    ip = DocType("Inpatient Record")
    it = DocType("Item")
    pe = DocType("Patient Encounter")
    sii = DocType("Sales Invoice Item")

    cash_ipd_cons_query = (
        frappe.qb.from_(ic)
        .inner_join(ip)
        .on(ic.parent == ip.name)
        .inner_join(it)
        .on(ic.consultation_item == it.name)
        .inner_join(pe)
        .on(ic.encounter == pe.name)
        .inner_join(sii)
        .on(ic.name == sii.reference_dn)
        .select(
            ic.date.as_("date"),
            ip.patient_appointment.as_("appointment_no"),
            ip.name.as_("bill_no"),
            ip.patient.as_("patient"),
            ip.patient_name.as_("patient_name"),
            ValueWrapper("In-Patient").as_("patient_type"),
            it.item_group.as_("service_type"),
            ic.consultation_item.as_("service_name"),
            ValueWrapper("Cash").as_("payment_method"),
            Count("*").as_("qty"),
            fn.Max(ic.rate).as_("rate"),
            Sum(sii.net_amount).as_("amount"),
            Sum(sii.amount - sii.net_amount).as_("discount_amount"),
            pe.medical_department.as_("department"),
            ic.healthcare_practitioner.as_("practitioner"),
            pe.healthcare_service_unit.as_("service_unit"),
            ic.modified.as_("date_modified"),
        )
        .where(
            (ip.company == filters.company)
            & (ic.date.between(filters.from_date, filters.to_date))
            & (ic.is_confirmed == 1)
            & (ic.hms_tz_invoiced == 1)
            & (
                (ip.insurance_coverage_plan.isnull())
                | (ip.insurance_coverage_plan == "")
            )
        )
        .groupby(
            ic.date,
            ip.patient,
            ip.name,
            ic.name,
            ic.consultation_item,
            ip.insurance_coverage_plan,
            ic.healthcare_practitioner,
        )
    )

    if filters.service_type:
        cash_ipd_cons_query = cash_ipd_cons_query.where(
            it.item_group == filters.service_type
        )

    cash_ipd_cons_data = cash_ipd_cons_query.run(as_dict=True)

    return cash_ipd_cons_data


def get_procedural_charges(filters):
    si = DocType("Sales Invoice")
    sii = DocType("Sales Invoice Item")
    sip = DocType("Sales Invoice Payment")
    pt = DocType("Patient")
    service_type_map = None
    if filters.service_type:
        service_type_map = sii.item_group == filters.service_type
    else:
        service_type_map = sii.item_group.isnotnull()
    procedural_charges = (
        frappe.qb.from_(si)
        .inner_join(sii)
        .on(si.name == sii.parent)
        .inner_join(sip)
        .on(si.name == sip.parent)
        .left_join(pt)
        .on(si.patient == pt.name)
        .select(
            si.posting_date.as_("date"),
            si.name.as_("bill_no"),
            Case()
            .when(si.patient.isnull(), "Outsider Customer")
            .else_(si.patient)
            .as_("patient"),
            Case()
            .when(si.patient.isnull(), si.customer_name)
            .else_(si.patient_name)
            .as_("patient_name"),
            Case()
            .when(pt.inpatient_record.isnull(), "Out-Patient")
            .else_("In-Patient")
            .as_("patient_type"),
            sii.item_group.as_("service_type"),
            sii.item_code.as_("service_name"),
            sip.mode_of_payment.as_("payment_method"),
            Sum(sii.qty).as_("qty"),
            Sum(sii.amount).as_("rate"),
            Sum(sii.amount).as_("amount"),
            Sum((sii.amount - sii.net_amount)).as_("discount_amount"),
            sii.net_amount.as_("net_amount"),
            Case().when(si.docstatus == 1, "Submitted").else_("Draft").as_("status"),
            sii.modified.as_("date_modified"),
        )
        .where(
            (si.company == filters.company)
            & si.posting_date.between(filters.from_date, filters.to_date)
            & (~si.status.isin(["Credit Note Issued", "Return"]))
            & (si.docstatus == 1)
            & (si.is_return == 0)
            & (sii.reference_dt.isnull())
            & (sii.reference_dn.isnull())
            & (sii.healthcare_practitioner.isnull())
            & (sii.sales_order.isnotnull())
            & service_type_map
        )
        .groupby(
            si.posting_date,
            si.patient,
            si.name,
            sii.item_code,
            sip.mode_of_payment,
        )
    ).run(as_dict=True)
    return procedural_charges


def get_cancelled_lab_items(filters):
    lreturn = DocType("LRPMT Returns")
    ireturn = DocType("Item Return")
    pe = DocType("Patient Encounter")
    lp = DocType("Lab Prescription")

    lab_item_query = (
        frappe.qb.from_(lreturn)
        .inner_join(ireturn)
        .on(lreturn.name == ireturn.parent)
        .inner_join(lp)
        .on(ireturn.child_name == lp.name)
        .inner_join(pe)
        .on(ireturn.encounter_no == pe.name)
        .select(
            fn.Date(lreturn.modified).as_("date"),
            lreturn.patient.as_("patient"),
            lreturn.patient_name.as_("patient_name"),
            Case()
            .when(lreturn.inpatient_record.isnull(), "Out-Patient")
            .else_("In-Patient")
            .as_("patient_type"),
            ireturn.item_name.as_("service_name"),
            Case()
            .when(
                (pe.insurance_coverage_plan.isnull())
                | (pe.insurance_coverage_plan == ""),
                "Cash",
            )
            .else_(pe.insurance_coverage_plan)
            .as_("payment_method"),
            ireturn.quantity.as_("qty"),
            lp.amount.as_("rate"),
            lp.amount.as_("amount"),
            ireturn.reference_doctype.as_("bill_doctype"),
            ireturn.reference_docname.as_("bill_no"),
            ireturn.encounter_no.as_("encounter_no"),
            ireturn.reason.as_("reason"),
            lreturn.name.as_("reference_no"),
            lreturn.appointment.as_("appointment_no"),
            lreturn.requested_by.as_("requested_by"),
            lreturn.approved_by.as_("approved_by"),
            lreturn.modified.as_("date_modified"),
        )
        .where(
            (lreturn.company == filters.company)
            & (lreturn.modified.between(filters.from_date, filters.to_date))
            & (lreturn.docstatus == 1)
            & (lp.is_cancelled == 1)
            & (ireturn.reference_doctype == "Lab Test")
            & (ireturn.encounter_no.isnotnull())
        )
    )

    if filters.get("payment_mode") and filters.get("payment_mode") != "Cash":
        lab_item_query = lab_item_query.where(
            (pe.insurance_company == filters.get("payment_mode")) & (lp.prescribe == 0)
        )

    if filters.get("payment_mode") and filters.get("payment_mode") == "Cash":
        lab_item_query = lab_item_query.where(
            # pick only prescribed items so as to include uncovered items from insurance encounters
            (lp.prescribe == 1)
        )

    lab_item_data = lab_item_query.run(as_dict=True)

    return lab_item_data


def get_cancelled_radiology_items(filters):
    lreturn = DocType("LRPMT Returns")
    ireturn = DocType("Item Return")
    pe = DocType("Patient Encounter")
    rpp = DocType("Radiology Procedure Prescription")

    radiology_item_query = (
        frappe.qb.from_(lreturn)
        .inner_join(ireturn)
        .on(lreturn.name == ireturn.parent)
        .inner_join(rpp)
        .on(ireturn.child_name == rpp.name)
        .inner_join(pe)
        .on(ireturn.encounter_no == pe.name)
        .select(
            fn.Date(lreturn.modified).as_("date"),
            lreturn.patient.as_("patient"),
            lreturn.patient_name.as_("patient_name"),
            Case()
            .when(lreturn.inpatient_record.isnull(), "Out-Patient")
            .else_("In-Patient")
            .as_("patient_type"),
            ireturn.item_name.as_("service_name"),
            Case()
            .when(
                (pe.insurance_coverage_plan.isnull())
                | (pe.insurance_coverage_plan == ""),
                "Cash",
            )
            .else_(pe.insurance_coverage_plan)
            .as_("payment_method"),
            ireturn.quantity.as_("qty"),
            rpp.amount.as_("rate"),
            rpp.amount.as_("amount"),
            ireturn.reference_doctype.as_("bill_doctype"),
            ireturn.reference_docname.as_("bill_no"),
            ireturn.encounter_no.as_("encounter_no"),
            ireturn.reason.as_("reason"),
            lreturn.name.as_("reference_no"),
            lreturn.appointment.as_("appointment_no"),
            lreturn.requested_by.as_("requested_by"),
            lreturn.approved_by.as_("approved_by"),
            lreturn.modified.as_("date_modified"),
        )
        .where(
            (lreturn.company == filters.company)
            & (lreturn.modified.between(filters.from_date, filters.to_date))
            & (lreturn.docstatus == 1)
            & (rpp.is_cancelled == 1)
            & (ireturn.reference_doctype == "Radiology Examination")
            & (ireturn.encounter_no.isnotnull())
        )
    )

    if filters.get("payment_mode") and filters.get("payment_mode") != "Cash":
        radiology_item_query = radiology_item_query.where(
            (pe.insurance_company == filters.get("payment_mode")) & (rpp.prescribe == 0)
        )

    if filters.get("payment_mode") and filters.get("payment_mode") == "Cash":
        radiology_item_query = radiology_item_query.where(
            # pick only prescribed items so as to include uncovered items from insurance encounters
            (rpp.prescribe == 1)
        )

    radiology_item_data = radiology_item_query.run(as_dict=True)

    return radiology_item_data


def get_cancelled_procedure_items(filters):
    lreturn = DocType("LRPMT Returns")
    ireturn = DocType("Item Return")
    pe = DocType("Patient Encounter")
    pp = DocType("Procedure Prescription")

    precedure_item_query = (
        frappe.qb.from_(lreturn)
        .inner_join(ireturn)
        .on(lreturn.name == ireturn.parent)
        .inner_join(pp)
        .on(ireturn.child_name == pp.name)
        .inner_join(pe)
        .on(ireturn.encounter_no == pe.name)
        .select(
            fn.Date(lreturn.modified).as_("date"),
            lreturn.patient.as_("patient"),
            lreturn.patient_name.as_("patient_name"),
            Case()
            .when(lreturn.inpatient_record.isnull(), "Out-Patient")
            .else_("In-Patient")
            .as_("patient_type"),
            ireturn.item_name.as_("service_name"),
            Case()
            .when(
                (pe.insurance_coverage_plan.isnull())
                | (pe.insurance_coverage_plan == ""),
                "Cash",
            )
            .else_(pe.insurance_coverage_plan)
            .as_("payment_method"),
            ireturn.quantity.as_("qty"),
            pp.amount.as_("rate"),
            pp.amount.as_("amount"),
            ireturn.reference_doctype.as_("bill_doctype"),
            ireturn.reference_docname.as_("bill_no"),
            ireturn.encounter_no.as_("encounter_no"),
            ireturn.reason.as_("reason"),
            lreturn.name.as_("reference_no"),
            lreturn.appointment.as_("appointment_no"),
            lreturn.requested_by.as_("requested_by"),
            lreturn.approved_by.as_("approved_by"),
            lreturn.modified.as_("date_modified"),
        )
        .where(
            (lreturn.company == filters.company)
            & (lreturn.modified.between(filters.from_date, filters.to_date))
            & (lreturn.docstatus == 1)
            & (pp.is_cancelled == 1)
            & (ireturn.reference_doctype == "Clinical Procedure")
            & (ireturn.encounter_no.isnotnull())
        )
    )
    if filters.get("payment_mode") and filters.get("payment_mode") != "Cash":
        precedure_item_query = precedure_item_query.where(
            (pe.insurance_company == filters.get("payment_mode")) & (pp.prescribe == 0)
        )

    if filters.get("payment_mode") and filters.get("payment_mode") == "Cash":
        precedure_item_query = precedure_item_query.where(
            # pick only prescribed items so as to include uncovered items from insurance encounters
            (pp.prescribe == 1)
        )

    procedure_item_data = precedure_item_query.run(as_dict=True)

    return procedure_item_data


def get_cancelled_drug_items(filters):
    lreturn = DocType("LRPMT Returns")
    mreturn = DocType("Medication Return")
    pe = DocType("Patient Encounter")
    dp = DocType("Drug Prescription")

    drug_item_query = (
        frappe.qb.from_(lreturn)
        .inner_join(mreturn)
        .on(lreturn.name == mreturn.parent)
        .inner_join(dp)
        .on(mreturn.child_name == dp.name)
        .inner_join(pe)
        .on(mreturn.encounter_no == pe.name)
        .select(
            fn.Date(lreturn.modified).as_("date"),
            lreturn.patient.as_("patient"),
            lreturn.patient_name.as_("patient_name"),
            Case()
            .when(lreturn.inpatient_record.isnull(), "Out-Patient")
            .else_("In-Patient")
            .as_("patient_type"),
            mreturn.drug_name.as_("service_name"),
            Case()
            .when(
                (pe.insurance_coverage_plan.isnull())
                | (pe.insurance_coverage_plan == ""),
                "Cash",
            )
            .else_(pe.insurance_coverage_plan)
            .as_("payment_method"),
            mreturn.quantity_prescribed.as_("qty"),
            dp.amount.as_("rate"),
            (mreturn.quantity_prescribed * dp.amount).as_("amount"),
            ValueWrapper("Delivery Note").as_("bill_doctype"),
            mreturn.delivery_note_no.as_("bill_no"),
            mreturn.encounter_no.as_("encounter_no"),
            mreturn.reason.as_("reason"),
            lreturn.name.as_("reference_no"),
            lreturn.appointment.as_("appointment_no"),
            lreturn.requested_by.as_("requested_by"),
            lreturn.approved_by.as_("approved_by"),
            lreturn.modified.as_("date_modified"),
        )
        .where(
            (lreturn.company == filters.company)
            & (lreturn.modified.between(filters.from_date, filters.to_date))
            & (lreturn.docstatus == 1)
            & (dp.is_cancelled == 1)
            & (mreturn.encounter_no.isnotnull())
        )
    )

    if filters.get("payment_mode") and filters.get("payment_mode") != "Cash":
        drug_item_query = drug_item_query.where(
            (pe.insurance_company == filters.get("payment_mode")) & (dp.prescribe == 0)
        )

    if filters.get("payment_mode") and filters.get("payment_mode") == "Cash":
        drug_item_query = drug_item_query.where(
            # pick only prescribed items so as to include uncovered items from insurance encounters
            (dp.prescribe == 1)
        )

    drug_item_data = drug_item_query.run(as_dict=True)

    return drug_item_data


def get_cancelled_data(filters):
    cancelled_data = []

    if not filters.get("bill_doctype"):
        cancelled_data += get_cancelled_lab_items(filters)
        cancelled_data += get_cancelled_radiology_items(filters)
        cancelled_data += get_cancelled_procedure_items(filters)
        cancelled_data += get_cancelled_drug_items(filters)

    elif filters.get("bill_doctype") == "Lab Test":
        cancelled_data += get_cancelled_lab_items(filters)

    elif filters.get("bill_doctype") == "Radiology Examination":
        cancelled_data += get_cancelled_radiology_items(filters)

    elif filters.get("bill_doctype") == "Clinical Procedure":
        cancelled_data += get_cancelled_procedure_items(filters)

    elif filters.get("bill_doctype") == "Delivery Note":
        cancelled_data += get_cancelled_drug_items(filters)

    return cancelled_data


@frappe.whitelist()
def get_payment_modes(company):
    payment_modes = ["", "Cash"]
    if not company:
        return payment_modes

    insurance_companies = frappe.get_all(
        "Healthcare Insurance Company",
        filters={"company": company, "disabled": 0},
        pluck="name",
    )

    return payment_modes + sorted(insurance_companies)
