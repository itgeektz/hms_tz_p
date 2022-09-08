# -*- coding: utf-8 -*-
# Copyright (c) 2020, Aakvatech and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe import _
from hms_tz.nhif.api.healthcare_utils import create_delivery_note_from_LRPT
from hms_tz.nhif.api.healthcare_utils import get_restricted_LRPT


def validate(doc, methd):
    if not doc.prescribe:
        is_restricted = get_restricted_LRPT(doc)
        doc.is_restricted = is_restricted


def on_submit(doc, methd):
    update_radiology_procedure_prescription(doc)
    create_delivery_note(doc)


def create_delivery_note(doc):
    if doc.ref_doctype and doc.ref_docname and doc.ref_doctype == "Patient Encounter":
        patient_encounter_doc = frappe.get_doc(doc.ref_doctype, doc.ref_docname)
        create_delivery_note_from_LRPT(doc, patient_encounter_doc)


def update_radiology_procedure_prescription(doc):
    if doc.ref_doctype == "Patient Encounter":
        encounter_doc = frappe.get_doc(doc.ref_doctype, doc.ref_docname)
        for row in encounter_doc.radiology_procedure_prescription:
            if row.radiology_examination_template == doc.radiology_examination_template:
                frappe.db.set_value(
                    row.doctype,
                    row.name,
                    {"radiology_examination": doc.name, "delivered_quantity": 1},
                )
