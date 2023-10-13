# Copyright (c) 2022, Aakvatech and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.query_builder import DocType
from frappe.query_builder.functions import Count



def execute(filters=None):
    if not filters:
        return

    columns = get_columns()
    records = get_data(filters)
<<<<<<< HEAD
=======
    if len(records) == 0:
        frappe.msgprint(_("No records found for the selected filters"))
        return [], []
>>>>>>> d76f58db (feat: add column 'claim status', add filter of 'patient type' change report to use frappe qeury builder and pypika)

    data = sorted(
        records,
        key=lambda x: (x["appointment_date"], x["patient"], x["authorization_number"]),
    )

    return columns, data


def get_columns():
    return [
        {
            "fieldname": "appointment_date",
            "label": _("Appointment Date"),
            "fieldtype": "Date",
        },
        {"fieldname": "patient", "label": _("Patient"), "fieldtype": "Data"},
        {"fieldname": "patient_name", "label": _("Patient Name"), "fieldtype": "Data"},
        {
            "fieldname": "appointment_no",
            "label": _("AppointmentNo"),
            "fieldtype": "Data",
        },
        {
            "fieldname": "authorization_number",
            "label": _("AuthorizationNo"),
            "fieldtype": "Data",
        },
        {
            "fieldname": "appointment_status",
            "label": _("Appointment Status"),
            "fieldtype": "Data",
        },
        {"fieldname": "encounter", "label": _("Last Encounter"), "fieldtype": "Data"},
        {
            "fieldname": "encounter_status",
            "label": _("Status of Last Encounter"),
            "fieldtype": "Data",
        },
        {
<<<<<<< HEAD
=======
            "fieldname": "inpatient_record",
            "label": _("Inpatient Record"),
            "fieldtype": "Data",
        },
        {
>>>>>>> d76f58db (feat: add column 'claim status', add filter of 'patient type' change report to use frappe qeury builder and pypika)
            "fieldname": "inpatient_status",
            "label": _("Inpatient Status"),
            "fieldtype": "Data",
        },
        {
<<<<<<< HEAD
            "fieldname": "nhif_claim_no",
=======
            "fieldname": "nhif_patient_claim",
>>>>>>> d76f58db (feat: add column 'claim status', add filter of 'patient type' change report to use frappe qeury builder and pypika)
            "label": _("NHIF Patient Claim"),
            "fieldtype": "Data",
        },
        {
            "fieldname": "signature",
            "label": _("Signature Captured"),
            "fieldtype": "Data",
        },
<<<<<<< HEAD
    ]


def get_data(filters):
    nhif_records = []
    nhif_appointments = []
    appointment_nos, patient_details = get_encounter_details(filters)

    nhif_claims = frappe.get_all(
        "NHIF Patient Claim",
        filters={
            "patient_appointment": ["in", appointment_nos],
            "company": filters.company,
        },
        fields=["patient_appointment", "patient", "name", "patient_signature"],
        order_by="attendance_date",
    )
    if not nhif_claims:
        return patient_details

    for d in patient_details:
        for claim in nhif_claims:
            if d["appointment_no"] == claim["patient_appointment"]:
                nhif_appointments.append(d["appointment_no"])

                if claim["patient_signature"]:
                    signature = "Yes"
                else:
                    signature = ""

                nhif_records.append(
                    {
                        "appointment_date": d["appointment_date"],
                        "patient": d["patient"],
                        "patient_name": d["patient_name"],
                        "appointment_no": d["appointment_no"],
                        "authorization_number": d["authorization_number"],
                        "appointment_status": d["appointment_status"],
                        "encounter": d["encounter"] or "",
                        "encounter_status": d["encounter_status"] or "",
                        "inpatient_status": d["ipd_status"] or "",
                        "nhif_claim_no": claim["name"] or "",
                        "signature": signature,
                    }
                )

        if d["appointment_no"] not in nhif_appointments:
            nhif_records.append(
                {
                    "appointment_date": d["appointment_date"],
                    "patient": d["patient"],
                    "patient_name": d["patient_name"],
                    "appointment_no": d["appointment_no"],
                    "authorization_number": d["authorization_number"],
                    "appointment_status": d["appointment_status"],
                    "encounter": d["encounter"] or "",
                    "encounter_status": d["encounter_status"] or "",
                    "inpatient_status": d["ipd_status"] or "",
                    "nhif_claim_no": "",
                    "signature": "",
                }
            )

    return nhif_records


def get_encounter_details(filters):
    appointment_list = []
    appointment_nos, appointments = get_appointment_details(filters)

    encounters = frappe.get_all(
        "Patient Encounter",
        filters={
            "appointment": ["in", appointment_nos],
            "company": filters.company,
            "duplicated": 0,
            "insurance_company": "NHIF",
        },
        fields=["appointment", "patient", "name", "docstatus"],
        order_by="encounter_date",
    )
    if not encounters:
        return appointment_nos, appointments

    encounter_details = []
    for appointment in appointments:
        for enc in encounters:
            if appointment["appointment_no"] == enc.appointment:
                appointment_list.append(appointment["appointment_no"])

                status = ""
                if enc.docstatus == 0:
                    status += "Draft"
                if enc.docstatus == 1:
                    status += "Submitted"
                if enc.docstatus == 2:
                    status += "Cancelled"

                appointment.update({"encounter": enc.name, "encounter_status": status})
                encounter_details.append(appointment)

        if appointment["appointment_no"] not in appointment_list:
            appointment.update({"encounter": "", "encounter_status": ""})
            encounter_details.append(appointment)

    return appointment_nos, encounter_details


def get_appointment_details(filters):
    name_list, entries = [], []
    appointment_list = []
    conditions = get_conditions(filters)

    appointments = frappe.get_all(
        "Patient Appointment",
        filters=conditions,
        fields=[
            "name",
            "patient",
            "patient_name",
            "appointment_date",
            "status",
            "authorization_number",
        ],
        order_by="appointment_date",
    )
    if not appointments:
        frappe.throw(
            "No Appointment(s) Found for the filters: #{0}, #{1} and #{2}".format(
                frappe.bold(filters.date),
                frappe.bold(filters.company),
                frappe.bold(filters.status),
            )
        )

    for pa in appointments:
        name_list.append(pa["name"])
        appointment_list.append(
            {
                "appointment_date": pa["appointment_date"],
                "patient": pa["patient"],
                "patient_name": pa["patient_name"],
                "appointment_no": pa["name"],
                "authorization_number": pa["authorization_number"],
                "appointment_status": pa["status"],
            }
        )

    inpatient_records = frappe.get_all(
        "Inpatient Record",
        filters={"patient_appointment": ["in", name_list], "insurance_company": "NHIF"},
        fields=["status", "patient_appointment"],
    )

    appointment_details = []
    for appointment in appointment_list:
        if inpatient_records:
            for record in inpatient_records:
                if appointment["appointment_no"] == record.patient_appointment:
                    entries.append(appointment["appointment_no"])
                    appointment["ipd_status"] = record.status
                    appointment_details.append(appointment)

        if appointment["appointment_no"] not in entries:
            appointment["ipd_status"] = ""
            appointment_details.append(appointment)

    return name_list, appointment_details


def get_conditions(filters):
    if filters:
        conditions = []
        if filters.from_date and filters.to_date:
            conditions.append(
                [
                    "appointment_date",
                    "between",
                    [filters.get("from_date"), filters.get("to_date")],
                ]
            )
        if filters.company:
            conditions.append(["company", "=", filters.company])
            conditions.append(["insurance_company", "=", "NHIF"])
        if filters.status == "Open":
            conditions.append(["status", "=", "Open"])
        if filters.status == "Closed":
            conditions.append(["status", "=", "Closed"])
        return conditions
=======
        {
            "fieldname": "claim_status",
            "label": _("Claim Status"),
            "fieldtype": "Data",
        },
    ]


def get_appointment_data(filters):
    pa = DocType("Patient Appointment")
    ip = DocType("Inpatient Record")
    npc = DocType("NHIF Patient Claim")

    status_map = None
    if filters.status == "Open":
        status_map = pa.status == "Open"
    elif filters.status == "Closed":
        status_map = pa.status == "Closed"
    elif filters.status == "Scheduled":
        status_map = pa.status == "Scheduled"
    elif filters.status == "Cancelled":
        status_map = pa.status == "Cancelled"
    else:
        status_map = pa.status.isnotnull()

    q = (
        frappe.qb.from_(pa)
        .left_join(npc)
        .on((pa.nhif_patient_claim == npc.name))
        .select(
            pa.name.as_("appointment_no"),
            pa.patient,
            pa.patient_name,
            pa.appointment_date,
            pa.status.as_("appointment_status"),
            pa.authorization_number,
            pa.nhif_patient_claim,
            pa.coverage_plan_card_number,
            npc.patient_signature.as_("patient_signature"),
            npc.docstatus,
        )
        .where(
            (pa.appointment_date.between(filters.from_date, filters.to_date))
            & (pa.company == filters.company)
            & (pa.insurance_company.like("NHIF"))
            & (status_map)
        )
        .orderby(pa.appointment_date)
    )
    if filters.patient_type == "In-patient":
        q = q.inner_join(ip).on(
            (pa.name == ip.patient_appointment) & (ip.insurance_company.like("NHIF"))
        )
        q = q.select(
            ip.name.as_("inpatient_record"),
            ip.status.as_("inpatient_status"),
        )
    if filters.patient_type == "Out-patient":
        inpatient_appointmens = (
            frappe.qb.from_(ip)
            .select(ip.patient_appointment)
            .where(
                (ip.insurance_company.like("NHIF"))
                & (ip.patient_appointment.isnotnull())
                & (ip.scheduled_date.between(filters.from_date, filters.to_date))
            )
            .orderby(ip.scheduled_date)
        ).run(as_dict=True)
        q = q.where(
            (~pa.name.isin([d.patient_appointment for d in inpatient_appointmens]))
        )

    if not filters.patient_type:
        q = q.left_join(ip).on(
            (pa.name == ip.patient_appointment) & (ip.insurance_company.like("NHIF"))
        )
        q = q.select(
            ip.name.as_("inpatient_record"),
            ip.status.as_("inpatient_status"),
        )
    appointment_data = q.run(as_dict=True)

    return appointment_data


def get_repeated_auth_no(filters):
    pa = DocType("Patient Appointment")

    status_map = None
    if filters.status == "Open":
        status_map = pa.status == "Open"
    elif filters.status == "Closed":
        status_map = pa.status == "Closed"
    elif filters.status == "Scheduled":
        status_map = pa.status == "Scheduled"
    elif filters.status == "Cancelled":
        status_map = pa.status == "Cancelled"
    else:
        status_map = pa.status.isnotnull()

    q = (
        frappe.qb.from_(pa)
        .select(
            pa.patient,
            pa.coverage_plan_card_number,
            pa.authorization_number,
            Count(pa.name).as_("count"),
        )
        .where(
            (pa.appointment_date.between(filters.from_date, filters.to_date))
            & (pa.company == filters.company)
            & (pa.insurance_company.like("NHIF"))
            & (status_map)
        )
        .groupby(pa.patient, pa.coverage_plan_card_number, pa.authorization_number)
    )
    repeated_auth_no = q.run(as_dict=True)
    return repeated_auth_no


def get_encounter_data(filter, appointment_nos):
    pe = DocType("Patient Encounter")

    q = (
        frappe.qb.from_(pe)
        .select(
            pe.patient,
            pe.docstatus,
            pe.appointment,
            pe.name.as_("encounter"),
        )
        .where(
            (pe.appointment.isin(appointment_nos))
            & (pe.company == filter.company)
            & (pe.duplicated == 0)
        )
        .orderby(pe.encounter_date)
    )
    encounter_data = q.run(as_dict=True)
    return encounter_data


def get_data(filters):
    appointment_list = []

    appointment_data = get_appointment_data(filters)
    auth_details = get_repeated_auth_no(filters)
    if len(appointment_data) == 0:
        return []

    appointment_nos = [d.appointment_no for d in appointment_data]
    for row in appointment_data:
        if row.nhif_patient_claim:
            status = None
            if row.docstatus == 0:
                status = "Draft"
            if row.docstatus == 1:
                status = "Submitted"
            if row.docstatus == 2:
                status = "Cancelled"
            row.claim_status = status
        if row.patient_signature:
            row.signature = "Yes"
        else:
            row.signature = ""

        for auth in auth_details:
            if (
                auth.count > 1
                and row.patient == auth.patient
                and row.authorization_number == auth.authorization_number
                and row.coverage_plan_card_number == auth.coverage_plan_card_number
            ):
                row.repeated_auth_no = True
        appointment_list.append(row)

    patient_encounter_data = get_encounter_data(filters, appointment_nos)
    if len(patient_encounter_data) == 0:
        return appointment_list

    encounter_details = []
    for appointment in appointment_list:
        for encounter in patient_encounter_data:
            if (
                appointment.patient == encounter.patient
                and appointment.appointment_no == encounter.appointment
            ):
                status = None
                if encounter.docstatus == 0:
                    status = "Draft"
                if encounter.docstatus == 1:
                    status = "Submitted"
                if encounter.docstatus == 2:
                    status = "Cancelled"

                appointment.encounter = encounter.encounter
                appointment.encounter_status = status

        encounter_details.append(appointment)

    return encounter_details
>>>>>>> d76f58db (feat: add column 'claim status', add filter of 'patient type' change report to use frappe qeury builder and pypika)
