# -*- coding: utf-8 -*-
# Copyright (c) 2020, Aakvatech and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe import _
from hms_tz.nhif.api.healthcare_utils import update_dimensions


def validate(doc, method):
    update_dimensions(doc)


def create_healthcare_docs(doc, method):
    for item in doc.items:
        if item.reference_dt:
            if item.reference_dt == "Healthcare Service Order":
                hso_doc = frappe.get_doc(
                    "Healthcare Service Order", item.reference_dn)
                if hso_doc.insurance_subscription and hso_doc.prescribed:
                    return
                if hso_doc.order_doctype == "Lab Test Template":
                    create_lab_test(hso_doc)
                elif hso_doc.order_doctype == "Radiology Examination Template":
                    create_radiology_examination(hso_doc)


def create_lab_test(hso_doc):
    if not hso_doc.order:
        return
    ltt_doc = frappe.get_doc("Lab Test Template", hso_doc.order)
    patient_sex = frappe.get_value("Patient", hso_doc.patient, "sex")

    doc = frappe.new_doc('Lab Test')
    doc.patient = hso_doc.patient
    doc.patient_sex = patient_sex
    doc.company = hso_doc.company
    doc.template = ltt_doc.name
    doc.practitioner = hso_doc.ordered_by
    doc.source = hso_doc.source
    doc.ref_doctype = hso_doc.doctype
    doc.ref_docname = hso_doc.name
    doc.invoiced = 1

    # for entry in ltt_doc.lab_test_groups:
    #     doc.append('normal_test_items', {
    #         'lab_test_name': entry.lab_test_description,
    #     })

    doc.save(ignore_permissions=True)
    if doc.get('name'):
        frappe.msgprint(_('Lab Test {0} created successfully.').format(
            frappe.bold(doc.name)))


def create_radiology_examination(hso_doc):
    if not hso_doc.order:
        return
    doc = frappe.new_doc('Radiology Examination')
    doc.patient = hso_doc.patient
    doc.company = hso_doc.company
    doc.radiology_examination_template = hso_doc.order
    doc.practitioner = hso_doc.ordered_by
    doc.source = hso_doc.source
    doc.medical_department = frappe.get_value(
        "Radiology Examination Template", hso_doc.order, "medical_department")
    doc.ref_doctype = hso_doc.doctype
    doc.ref_docname = hso_doc.name
    doc.invoiced = 1

    doc.save(ignore_permissions=True)

    hso_doc.invoiced = 1
    hso_doc.save(ignore_permissions=True)

    if doc.get('name'):
        frappe.msgprint(_('Radiology Examination {0} created successfully.').format(
            frappe.bold(doc.name)))
