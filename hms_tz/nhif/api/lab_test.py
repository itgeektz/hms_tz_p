# -*- coding: utf-8 -*-
# Copyright (c) 2020, Aakvatech and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe import _
from hms_tz.nhif.api.healthcare_utils import (
    create_delivery_note_from_LRPT,
    get_restricted_LRPT,
)
from frappe.utils import getdate
import dateutil


def validate(doc, method):
    is_restricted = get_restricted_LRPT(doc)
    doc.is_restricted = is_restricted
    set_normals(doc)

def set_normals(doc):
    dob = frappe.get_value("Patient", doc.patient, "dob")
    age = dateutil.relativedelta.relativedelta(getdate(), dob).years
    for row in doc.normal_test_items:
        if not row.result_value:
            continue
        normals = get_normals(row.lab_test_name, age, doc.patient_sex)
        if normals:
            row.min_normal = normals.get("min")
            row.max_normal = normals.get("max")
            row.text_normal = normals.get("text")

            data_normals = calc_data_normals(normals, row.result_value)
            row.detailed_normal_range = data_normals["detailed_normal_range"]
            row.result_status = data_normals["result_status"]

def calc_data_normals(data, value):
    data = frappe._dict(data)
    value = float(value)
    result = {
        "detailed_normal_range": "",
        "result_status": ""
    }

    if (data.min and not data.max):
        result["detailed_normal_range"] = "> " + str(data.min)
        if (value > data.min):
            result["result_status"] = "N"
        else:
            result["result_status"] = "L"
    elif (not data.min and data.max):
        result["detailed_normal_range"] = "< " + str(data.max)
        if (value < data.max):
            result["result_status"] = "N"
        else:
            result["result_status"] = "H"
    elif (data.min and data.max):
        result["detailed_normal_range"] = str(data.min) + " - " + str(data.max)
        if (value > data.min and value < data.max):
            result["result_status"] = "N"
        elif (value < data.min):
            result["result_status"] = "L"
        elif (value > data.max):
            result["result_status"] = "H"

    if (data.text):
        if (result["detailed_normal_range"]):
            result["detailed_normal_range"] += " / "

        result["detailed_normal_range"] += data.text

    return result

@frappe.whitelist()
def get_normals(lab_test_name, patient_age, patient_sex):
    data = {}
    doc = get_lab_test_template(lab_test_name)
    if not doc:
        return data
    if float(patient_age) < 3:
        data["min"] = doc.i_min_range
        data["max"] = doc.i_max_range
        data["text"] = doc.i_text
    elif float(patient_age) < 12:
        data["min"] = doc.c_min_range
        data["max"] = doc.c_max_range
        data["text"] = doc.c_text
    else:
        if patient_sex == "Male":
            data["min"] = doc.m_min_range
            data["max"] = doc.m_max_range
            data["text"] = doc.m_text
        elif patient_sex == "Female":
            data["min"] = doc.f_min_range
            data["max"] = doc.f_max_range
            data["text"] = doc.f_text

    return data


def get_lab_test_template(lab_test_name):
    template_id = frappe.db.exists(
        "Lab Test Template", {"lab_test_name": lab_test_name}
    )
    if template_id:
        return frappe.get_doc("Lab Test Template", template_id)
    return False


def on_submit(doc, methd):
    create_delivery_note(doc)


def create_delivery_note(doc):
    if doc.ref_doctype and doc.ref_docname and doc.ref_doctype == "Patient Encounter":
        patient_encounter_doc = frappe.get_doc(doc.ref_doctype, doc.ref_docname)
        create_delivery_note_from_LRPT(doc, patient_encounter_doc)


def after_insert(doc, methd):
    create_sample_collection(doc)


def on_trash(doc, methd):
    sample_list = frappe.get_all(
        "Sample Collection",
        filters={
            "ref_doctype": doc.doctype,
            "ref_docname": doc.name,
        },
    )
    for item in sample_list:
        frappe.delete_doc("Sample Collection", item.name)


def create_sample_collection(doc):
    if not doc.template:
        return
    template = frappe.get_doc("Lab Test Template", doc.template)
    if not template.sample_qty or not template.sample:
        return

    sample_doc = frappe.new_doc("Sample Collection")
    sample_doc.patient = doc.patient
    sample_doc.patient_name = doc.patient_name
    sample_doc.patient_age = doc.patient_age
    sample_doc.patient_sex = doc.patient_sex
    sample_doc.company = doc.company
    sample_doc.sample = template.sample
    sample_doc.sample_uom = template.sample_uom
    sample_doc.sample_qty = template.sample_qty
    sample_doc.sample_details = template.sample_details
    sample_doc.ref_doctype = doc.doctype
    sample_doc.ref_docname = doc.name

    sample_doc.flags.ignore_permissions = True
    sample_doc.insert()
    frappe.msgprint(
        _("Sample Collection created {0}").format(sample_doc.name), alert=True
    )
