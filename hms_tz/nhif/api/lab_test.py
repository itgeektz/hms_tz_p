# -*- coding: utf-8 -*-
# Copyright (c) 2020, Aakvatech and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe import _
from hms_tz.nhif.api.healthcare_utils import create_delivery_note_from_LRPT, get_restricted_LRPT


def validate(doc, methd):
    is_restricted = get_restricted_LRPT(doc)
    doc.is_restricted = is_restricted


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
        'Lab Test Template', {'lab_test_name': lab_test_name})
    if template_id:
        return frappe.get_doc('Lab Test Template', template_id)
    return False


def on_submit(doc, methd):
    create_delivery_note(doc)


def create_delivery_note(doc):
    if doc.ref_doctype and doc.ref_docname and doc.ref_doctype == "Patient Encounter":
        patient_encounter_doc = frappe.get_doc(
            doc.ref_doctype, doc.ref_docname)
        create_delivery_note_from_LRPT(doc, patient_encounter_doc)


def after_insert(doc, methd):
    create_sample_collection(doc)


def on_trash(doc, methd):
    sample_list = frappe.get_all("Sample Collection", filters={
        "ref_doctype": doc.doctype,
        "ref_docname": doc.name,
    })
    for item in sample_list:
        frappe.delete_doc('Sample Collection', item.name)


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
    frappe.msgprint(_("Sample Collection created {0}").format(
        sample_doc.name), alert=True)
