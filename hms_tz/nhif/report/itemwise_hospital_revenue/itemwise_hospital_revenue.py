# Copyright (c) 2023, Aakvatech and contributors
# For license information, please see license.txt

import frappe
from pypika import Case, Field, Query, Table, functions as fn
from frappe.query_builder import DocType
from frappe.query_builder.functions import Sum, Count


def execute(filters=None):
    data = []
    columns = get_columns(filters)
    data = get_appointment_data(filters)
    data += get_lab_data(filters)
    data += get_radiology_data(filters)
    data += get_procedure_data(filters)
    data += get_drug_data(filters)
    data += get_therapy_data(filters)
    data += get_ipd_beds_data(filters)
    data += get_ipd_cons_data(filters)
    # data += get_procedural_charges(filters)
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
        {"fieldname": "bill_no", "label": "Bill No", "fieldtype": "Data", "width": 120},
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
            "fieldname": "amount",
            "label": "Amount",
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
    ]

    return columns


def get_appointment_data(filters):
    appointment = DocType("Patient Appointment")
    item = DocType("Item")
    sii = DocType("Sales Invoice Item")
    service_type_map = None
    if filters.service_type:
        service_type_map = item.item_group == filters.service_type
    else:
        service_type_map = item.item_group.isnotnull()

    appointment_data = (
        frappe.qb.from_(appointment)
        .inner_join(item)
        .on(appointment.billing_item == item.name)
        .left_join(sii)
        .on((appointment.name == sii.reference_dn) & (appointment.invoiced == 1))
        .select(
            appointment.appointment_date.as_("date"),
            appointment.name.as_("bill_no"),
            appointment.patient.as_("patient"),
            appointment.patient_name.as_("patient_name"),
            Case()
            .when(appointment.inpatient_record.isnull(), "Out-Patient")
            .else_("In-Patient")
            .as_("patient_type"),
            item.item_group.as_("service_type"),
            appointment.billing_item.as_("service_name"),
            Case()
            .when(appointment.mode_of_payment.isnull(), appointment.coverage_plan_name)
            .else_("Cash")
            .as_("payment_method"),
            Count("*").as_("qty"),
            Sum(appointment.paid_amount).as_("rate"),
            Sum(appointment.paid_amount).as_("amount"),
            Case()
            .when(
                appointment.ref_sales_invoice.isnotnull(),
                Sum(sii.amount - sii.net_amount),
            )
            .else_(0)
            .as_("discount_amount"),
            Case()
            .when(appointment.status == "Closed", "Submitted")
            .else_("Draft")
            .as_("status"),
            appointment.practitioner.as_("practitioner"),
            appointment.department.as_("department"),
            appointment.service_unit.as_("service_unit"),
        )
        .where(
            (appointment.company == filters.company)
            & (appointment.appointment_date.between(filters.from_date, filters.to_date))
            & (appointment.status != "Cancelled")
            & (appointment.follow_up == 0)
            & (appointment.has_no_consultation_charges == 0)
            & service_type_map
        )
        .groupby(
            appointment.appointment_date,
            appointment.patient,
            appointment.name,
            appointment.billing_item,
            Case()
            .when(appointment.mode_of_payment.isnull(), appointment.coverage_plan_name)
            .else_("Cash"),
            appointment.practitioner.as_("practitioner"),
            Case().when(appointment.status == "Closed", "Closed").else_("Open"),
        )
    ).run(as_dict=True)

    return appointment_data


def get_lab_data(filters):
    lab = DocType("Lab Test")
    lab_prescription = DocType("Lab Prescription")
    template = DocType("Lab Test Template")
    sii = DocType("Sales Invoice Item")
    service_type_map = None
    if filters.service_type:
        service_type_map = template.lab_test_group == filters.service_type
    else:
        service_type_map = template.lab_test_group.isnotnull()

    lab_data = (
        frappe.qb.from_(lab)
        .inner_join(lab_prescription)
        .on(lab.hms_tz_ref_childname == lab_prescription.name)
        .inner_join(template)
        .on(lab.template == template.name)
        .left_join(sii)
        .on(
            (lab.hms_tz_ref_childname == sii.reference_dn)
            & (lab_prescription.invoiced == 1)
            & (lab_prescription.sales_invoice_number == sii.parent)
        )
        .select(
            lab.result_date.as_("date"),
            lab.name.as_("bill_no"),
            lab.patient.as_("patient"),
            lab.patient_name.as_("patient_name"),
            Case()
            .when(lab.inpatient_record.isnull(), "Out-Patient")
            .else_("In-Patient")
            .as_("patient_type"),
            template.lab_test_group.as_("service_type"),
            lab.template.as_("service_name"),
            Case()
            .when(lab.prescribe == 1, "Cash")
            .else_(lab.hms_tz_insurance_coverage_plan)
            .as_("payment_method"),
            Count("*").as_("qty"),
            Sum(lab_prescription.amount).as_("rate"),
            Sum(lab_prescription.amount).as_("amount"),
            Case()
            .when(
                lab.prescribe == 1,
                Sum(sii.amount - sii.net_amount),
            )
            .else_(0)
            .as_("discount_amount"),
            Case().when(lab.docstatus == 1, "Submitted").else_("Draft").as_("status"),
            lab.practitioner.as_("practitioner"),
            lab.department.as_("department"),
            lab_prescription.department_hsu.as_("service_unit"),
        )
        .where(
            (lab.company == filters.company)
            & (lab.result_date.between(filters.from_date, filters.to_date))
            & ~lab.workflow_state.isin(["Not Serviced", "Submitted but Not Serviced"])
            & (lab.docstatus != 2)
            & (lab.ref_doctype == "Patient Encounter")
            & (lab.ref_docname.isnotnull())
            & (lab.ref_docname == lab_prescription.parent)
            & service_type_map
        )
        .groupby(
            lab.result_date,
            lab.patient,
            lab.name,
            lab.template,
            Case()
            .when(lab.prescribe == 1, "Cash")
            .else_(lab.hms_tz_insurance_coverage_plan),
            lab.practitioner,
            Case().when(lab.docstatus == 1, "Submitted").else_("Draft").as_("status"),
        )
    ).run(as_dict=True)

    return lab_data


def get_radiology_data(filters):
    rad = DocType("Radiology Examination")
    rad_prescription = DocType("Radiology Procedure Prescription")
    template = DocType("Radiology Examination Template")
    sii = DocType("Sales Invoice Item")
    service_type_map = None
    if filters.service_type:
        service_type_map = template.item_group == filters.service_type
    else:
        service_type_map = template.item_group.isnotnull()

    rad_data = (
        frappe.qb.from_(rad)
        .inner_join(rad_prescription)
        .on(rad.hms_tz_ref_childname == rad_prescription.name)
        .inner_join(template)
        .on(rad.radiology_examination_template == template.name)
        .left_join(sii)
        .on(
            (rad.hms_tz_ref_childname == sii.reference_dn)
            & (rad_prescription.invoiced == 1)
            & (rad_prescription.sales_invoice_number == sii.parent)
        )
        .select(
            rad.start_date.as_("date"),
            rad.name.as_("bill_no"),
            rad.patient.as_("patient"),
            rad.patient_name.as_("patient_name"),
            Case()
            .when(rad.inpatient_record.isnull(), "Out-Patient")
            .else_("In-Patient")
            .as_("patient_type"),
            template.item_group.as_("service_type"),
            rad.radiology_examination_template.as_("service_name"),
            Case()
            .when(rad.prescribe == 1, "Cash")
            .else_(rad.hms_tz_insurance_coverage_plan)
            .as_("payment_method"),
            Count("*").as_("qty"),
            Sum(rad_prescription.amount).as_("rate"),
            Sum(rad_prescription.amount).as_("amount"),
            Case()
            .when(
                rad.prescribe == 1,
                Sum(sii.amount - sii.net_amount),
            )
            .else_(0)
            .as_("discount_amount"),
            Case().when(rad.docstatus == 1, "Submitted").else_("Draft").as_("status"),
            rad.practitioner.as_("practitioner"),
            rad.medical_department.as_("department"),
            rad_prescription.department_hsu.as_("service_unit"),
        )
        .where(
            (rad.company == filters.company)
            & (rad.start_date.between(filters.from_date, filters.to_date))
            & ~rad.workflow_state.isin(["Not Serviced", "Submitted but Not Serviced"])
            & (rad.docstatus != 2)
            & (rad.ref_doctype == "Patient Encounter")
            & (rad.ref_docname.isnotnull())
            & (rad.ref_docname == rad_prescription.parent)
            & service_type_map
        )
        .groupby(
            rad.start_date,
            rad.patient,
            rad.name,
            rad.radiology_examination_template,
            Case()
            .when(rad.prescribe == 1, "Cash")
            .else_(rad.hms_tz_insurance_coverage_plan),
            rad.practitioner,
            Case().when(rad.docstatus == 1, "Submitted").else_("Draft"),
        )
    ).run(as_dict=True)

    return rad_data


def get_procedure_data(filters):
    procedure = DocType("Clinical Procedure")
    pp = DocType("Procedure Prescription")
    template = DocType("Clinical Procedure Template")
    sii = DocType("Sales Invoice Item")
    service_type_map = None
    if filters.service_type:
        service_type_map = template.item_group == filters.service_type
    else:
        service_type_map = template.item_group.isnotnull()
    procedure_data = (
        frappe.qb.from_(procedure)
        .inner_join(pp)
        .on(procedure.hms_tz_ref_childname == pp.name)
        .inner_join(template)
        .on(procedure.procedure_template == template.name)
        .left_join(sii)
        .on(
            (procedure.hms_tz_ref_childname == sii.reference_dn)
            & (pp.invoiced == 1)
            & (pp.sales_invoice_number == sii.parent)
        )
        .select(
            procedure.start_date.as_("date"),
            procedure.name.as_("bill_no"),
            procedure.patient.as_("patient"),
            procedure.patient_name.as_("patient_name"),
            Case()
            .when(procedure.inpatient_record.isnull(), "Out-Patient")
            .else_("In-Patient")
            .as_("patient_type"),
            template.item_group.as_("service_type"),
            procedure.procedure_template.as_("service_name"),
            Case()
            .when(procedure.prescribe == 1, "Cash")
            .else_(procedure.hms_tz_insurance_coverage_plan)
            .as_("payment_method"),
            Count("*").as_("qty"),
            Sum(pp.amount).as_("rate"),
            Sum(pp.amount).as_("amount"),
            Case()
            .when(
                procedure.prescribe == 1,
                sii.amount - sii.net_amount,
            )
            .else_(0)
            .as_("discount_amount"),
            Case()
            .when(procedure.docstatus == 1, "Submitted")
            .else_("Draft")
            .as_("status"),
            procedure.practitioner.as_("practitioner"),
            procedure.medical_department.as_("department"),
            pp.department_hsu.as_("service_unit"),
        )
        .where(
            (procedure.company == filters.company)
            & (procedure.start_date.between(filters.from_date, filters.to_date))
            & ~procedure.workflow_state.isin(
                ["Not Serviced", "Submitted but Not Serviced"]
            )
            & (procedure.docstatus != 2)
            & (procedure.ref_doctype == "Patient Encounter")
            & (procedure.ref_docname.isnotnull())
            & (procedure.ref_docname == pp.parent)
            & service_type_map
        )
        .groupby(
            procedure.start_date,
            procedure.patient,
            procedure.name,
            procedure.procedure_template,
            Case()
            .when(procedure.prescribe == 1, "Cash")
            .else_(procedure.hms_tz_insurance_coverage_plan),
            procedure.practitioner,
            Case().when(procedure.docstatus == 1, "Submitted").else_("Draft"),
        )
    ).run(as_dict=True)
    return procedure_data


def get_drug_data(filters):
    dn = DocType("Delivery Note")
    dni = DocType("Delivery Note Item")
    dp = DocType("Drug Prescription")
    md = DocType("Medication")
    si = DocType("Sales Invoice")
    sii = DocType("Sales Invoice Item")
    pe = DocType("Patient Encounter")
    service_type_map = None
    if filters.service_type:
        service_type_map = dni.item_group == filters.service_type
    else:
        service_type_map = dni.item_group.isnotnull()
    insurance_drug_data = (
        frappe.qb.from_(dn)
        .inner_join(dni)
        .on(dn.name == dni.parent)
        .inner_join(md)
        .on(dni.item_code == md.item)
        .inner_join(pe)
        .on(dn.reference_name == pe.name)
        .left_join(dp)
        .on(dni.name == dp.dn_detail & dp.is_cancelled == 0)
        .select(
            dn.posting_date.as_("date"),
            dn.name.as_("bill_no"),
            dn.patient.as_("patient"),
            dn.patient_name.as_("patient_name"),
            Case()
            .when(pe.inpatient_record.isnull(), "Out-Patient")
            .else_("In-Patient")
            .as_("patient_type"),
            md.item_group.as_("service_type"),
            dni.item_code.as_("service_name"),
            Case()
            .when(dn.coverage_plan_name.isnull(), "Cash")
            .else_(dn.coverage_plan_name)
            .as_("payment_method"),
            Sum(dni.qty).as_("qty"),
            Sum(dni.rate).as_("rate"),
            Sum((dni.qty * dni.rate)).as_("amount"),
            Sum(dni.discount_amount).as_("discount_amount"),
            Case().when(dn.docstatus == 1, "Submitted").else_("Draft").as_("status"),
            dn.healthcare_practitioner.as_("practitioner"),
            md.healthcare_service_order_category.as_("department"),
            dn.healthcare_service_unit.as_("service_unit"),
        )
        .where(
            (dn.company == filters.company)
            & (dn.posting_date.between(filters.from_date, filters.to_date))
            & (~dn.workflow_state.isin(["Not Serviced", "Submitted but Not Serviced"]))
            & (dn.docstatus != 2)
            & (dn.is_return == 0)
            & (dn.form_sales_invoice.isnull())
            & service_type_map
        )
        .groupby(
            dn.posting_date,
            dn.patient,
            dni.name,
            dni.item_code,
            Case()
            .when(dn.coverage_plan_name.isnull(), "Cash")
            .else_(dn.coverage_plan_name),
            dn.healthcare_practitioner,
            Case().when(dn.docstatus == 1, "Submitted").else_("Draft"),
        )
    ).run(as_dict=True)

    cash_drug_data = (
        frappe.qb.from_(dn)
        .inner_join(dni)
        .on(dn.name == dni.parent)
        .inner_join(md)
        .on(dni.item_code == md.item)
        .inner_join(si)
        .on(dn.form_sales_invoice == si.name)
        .inner_join(sii)
        .on(si.name == sii.parent)
        .left_join(pe)
        .on(dn.reference_name == pe.name)
        .select(
            dn.posting_date.as_("date"),
            dn.name.as_("bill_no"),
            Case()
            .when(dn.patient.isnull(), "Outsider Customer")
            .else_(dn.patient)
            .as_("patient"),
            Case()
            .when(dn.patient.isnull(), dn.customer_name)
            .else_(dn.patient_name)
            .as_("patient_name"),
            Case()
            .when(pe.inpatient_record.isnull(), "Out-Patient")
            .else_("In-Patient")
            .as_("patient_type"),
            md.item_group.as_("service_type"),
            dni.item_code.as_("service_name"),
            Case()
            .when(dni.si_detail.isnotnull(), "Cash")
            .else_(dn.coverage_plan_name)
            .as_("payment_method"),
            Sum(dni.qty).as_("qty"),
            Sum(dni.rate).as_("rate"),
            Sum(dni.qty * dni.rate).as_("amount"),
            Sum(sii.amount - sii.net_amount).as_("discount_amount"),
            Case().when(dn.docstatus == 1, "Submitted").else_("Draft").as_("status"),
            dni.healthcare_practitioner.as_("practitioner"),
            md.healthcare_service_order_category.as_("department"),
            dni.healthcare_service_unit.as_("service_unit"),
        )
        .where(
            (dn.company == filters.company)
            & (dn.posting_date.between(filters.from_date, filters.to_date))
            & (~dn.workflow_state.isin(["Not Serviced", "Submitted but Not Serviced"]))
            & (dn.docstatus != 2)
            & (dn.is_return == 0)
            & (dn.form_sales_invoice.isnotnull())
            & (~si.status.isin(["Credit Note Issued", "Return"]))
            & service_type_map
        )
        .groupby(
            dn.posting_date,
            dn.patient,
            dni.name,
            dni.item_code,
            Case().when(dni.si_detail.isnotnull(), "Cash").else_(dn.coverage_plan_name),
            dni.healthcare_practitioner,
            Case().when(dn.docstatus == 1, "Submitted").else_("Draft"),
        )
    ).run(as_dict=True)

    return insurance_drug_data + cash_drug_data


def get_therapy_data(filters):
    tp = DocType("Therapy Plan")
    tpd = DocType("Therapy Plan Detail")
    tt = DocType("Therapy Type")
    sii = DocType("Sales Invoice Item")
    pe = DocType("Patient Encounter")
    service_type_map = None
    if filters.service_type:
        service_type_map = tt.item_group == filters.service_type
    else:
        service_type_map = tt.item_group.isnotnull()
    therapy_data = (
        frappe.qb.from_(tp)
        .inner_join(pe)
        .on(tp.ref_docname == pe.name)
        .inner_join(tpd)
        .on(pe.name == tpd.parent)
        .inner_join(tt)
        .on(tpd.therapy_type == tt.name)
        .left_join(sii)
        .on((tpd.name == sii.reference_dn) & (tpd.sales_invoice_number == sii.parent))
        .select(
            tp.start_date.as_("date"),
            tp.name.as_("bill_no"),
            tp.patient.as_("patient"),
            tp.patient_name.as_("patient_name"),
            Case()
            .when(pe.inpatient_record.isnull(), "Out-Patient")
            .else_("In-Patient")
            .as_("patient_type"),
            tt.item_group.as_("service_type"),
            tpd.therapy_type.as_("service_name"),
            Case()
            .when(tpd.prescribe == 1, "Cash")
            .else_(tp.hms_tz_insurance_coverage_plan)
            .as_("payment_method"),
            Sum(tpd.no_of_sessions).as_("qty"),
            Sum(tpd.amount).as_("rate"),
            Sum(tpd.amount).as_("amount"),
            Case()
            .when(
                tpd.prescribe == 1,
                Sum(sii.amount - sii.net_amount),
            )
            .else_(0)
            .as_("discount_amount"),
            Case()
            .when(tp.status == "Completed", "Submitted")
            .else_("Draft")
            .as_("status"),
            pe.practitioner.as_("practitioner"),
            tt.medical_department.as_("department"),
            tpd.department_hsu.as_("service_unit"),
        )
        .where(
            (tp.company == filters.company)
            & (tp.start_date.between(filters.from_date, filters.to_date))
            & (tpd.is_cancelled != 1)
            & (tpd.is_not_available_inhouse != 1)
            & service_type_map
        )
        .groupby(
            tp.start_date,
            tp.patient,
            tp.name,
            tpd.therapy_type,
            Case()
            .when(tpd.prescribe == 1, "Cash")
            .else_(tp.hms_tz_insurance_coverage_plan),
            pe.practitioner,
            Case().when(tp.status == "Completed", "Submitted").else_("Draft"),
        )
    ).run(as_dict=True)
    return therapy_data


def get_ipd_beds_data(filters):
    io = DocType("Inpatient Occupancy")
    ip = DocType("Inpatient Record")
    hsu = DocType("Healthcare Service Unit")
    hsut = DocType("Healthcare Service Unit Type")
    sii = DocType("Sales Invoice Item")
    service_type_map = None
    if filters.service_type:
        service_type_map = hsut.item_group == filters.service_type
    else:
        service_type_map = hsut.item_group.isnotnull()
    ipd_beds_data = (
        frappe.qb.from_(io)
        .inner_join(ip)
        .on(io.parent == ip.name)
        .inner_join(hsu)
        .on(io.service_unit == hsu.name)
        .inner_join(hsut)
        .on(hsu.service_unit_type == hsut.name)
        .left_join(sii)
        .on(
            (io.name == sii.reference_dn)
            & (io.invoiced == 1)
            & (io.sales_invoice_number == sii.parent)
        )
        .select(
            fn.Date(io.check_in).as_("date"),
            ip.name.as_("bill_no"),
            ip.patient.as_("patient"),
            ip.patient_name.as_("patient_name"),
            Case()
            .when(io.is_confirmed == 1, "In-Patient")
            .else_("Out Patient")
            .as_("patient_type"),
            hsut.item_group.as_("service_type"),
            hsu.service_unit_type.as_("service_name"),
            Case()
            .when(ip.insurance_coverage_plan.isin(("", None)), "Cash")
            .else_(ip.insurance_coverage_plan)
            .as_("payment_method"),
            Count("*").as_("qty"),
            Sum(io.amount).as_("rate"),
            Sum(io.amount).as_("amount"),
            Case()
            .when(
                io.invoiced == 1,
                Sum(sii.amount - sii.net_amount),
            )
            .else_(0)
            .as_("discount_amount"),
            hsu.service_unit_type.as_("department"),
            hsu.parent_healthcare_service_unit.as_("service_unit"),
        )
        .where(
            (ip.company == filters.company)
            & (io.check_in.between(filters.from_date, filters.to_date))
            & (io.is_confirmed == 1)
            & service_type_map
        )
        .groupby(
            fn.Date(io.check_in),
            ip.patient,
            ip.name,
            hsu.service_unit_type,
            Case()
            .when(ip.insurance_coverage_plan.isin(("", None)), "Cash")
            .else_(ip.insurance_coverage_plan),
        )
    ).run(as_dict=True)
    return ipd_beds_data


def get_ipd_cons_data(filters):
    ic = DocType("Inpatient Consultancy")
    ip = DocType("Inpatient Record")
    it = DocType("Item")
    pe = DocType("Patient Encounter")
    sii = DocType("Sales Invoice Item")
    service_type_map = None
    if filters.service_type:
        service_type_map = it.item_group == filters.service_type
    else:
        service_type_map = it.item_group.isnotnull()
    ipd_cons_data = (
        frappe.qb.from_(ic)
        .inner_join(ip)
        .on(ic.parent == ip.name)
        .inner_join(it)
        .on(ic.consultation_item == it.name)
        .inner_join(pe)
        .on(ic.encounter == pe.name)
        .left_join(sii)
        .on(
            (ic.name == sii.reference_dn)
            & (ic.hms_tz_invoiced == 1)
            & (ic.sales_invoice_number == sii.parent)
        )
        .select(
            ic.date.as_("date"),
            ip.name.as_("bill_no"),
            ip.patient.as_("patient"),
            ip.patient_name.as_("patient_name"),
            Case()
            .when(ic.is_confirmed == 1, "In-Patient")
            .else_("Out Patient")
            .as_("patient_type"),
            it.item_group.as_("service_type"),
            ic.consultation_item.as_("service_name"),
            Case()
            .when(ip.insurance_coverage_plan.isin(("", None)), "Cash")
            .else_(ip.insurance_coverage_plan)
            .as_("payment_method"),
            Count("*").as_("qty"),
            Sum(ic.rate).as_("rate"),
            Sum(ic.rate).as_("amount"),
            Case()
            .when(
                ic.hms_tz_invoiced == 1,
                sii.amount - sii.net_amount,
            )
            .else_(0)
            .as_("discount_amount"),
            pe.medical_department.as_("department"),
            ic.healthcare_practitioner.as_("practitioner"),
            pe.healthcare_service_unit.as_("service_unit"),
        )
        .where(
            (ip.company == filters.company)
            & (ic.date.between(filters.from_date, filters.to_date))
            & (ic.is_confirmed == 1)
            & service_type_map
        )
        .groupby(
            ic.date,
            ip.patient,
            ip.name,
            ic.consultation_item,
            Case()
            .when(ip.insurance_coverage_plan.isin(("", None)), "Cash")
            .else_(ip.insurance_coverage_plan),
            ic.healthcare_practitioner,
        )
    ).run(as_dict=True)
    return ipd_cons_data


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
