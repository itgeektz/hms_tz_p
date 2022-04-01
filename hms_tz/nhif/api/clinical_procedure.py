# -*- coding: utf-8 -*-
# Copyright (c) 2020, Aakvatech and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe import _
from hms_tz.nhif.api.healthcare_utils import create_delivery_note_from_LRPT
from hms_tz.nhif.api.healthcare_utils import (
    create_delivery_note_from_LRPT,
    get_restricted_LRPT,
)
from hms_tz.hms_tz.doctype.clinical_procedure.clinical_procedure import insert_clinical_procedure_to_medical_record


def validate(doc, methd):
    if not doc.prescribe:
        is_restricted = get_restricted_LRPT(doc)
        doc.is_restricted = is_restricted

def on_submit(doc, methd):
    update_procedure_prescription(doc)
    insert_clinical_procedure_to_medical_record(doc)
    create_delivery_note(doc)


def create_delivery_note(doc):
    if doc.ref_doctype and doc.ref_docname and doc.ref_doctype == "Patient Encounter":
        patient_encounter_doc = frappe.get_doc(doc.ref_doctype, doc.ref_docname)
        create_delivery_note_from_LRPT(doc, patient_encounter_doc)

def update_procedure_prescription(doc):
    if doc.ref_doctype == "Patient Encounter":
        encounter_doc = frappe.get_doc(doc.ref_doctype, doc.ref_docname)
        for row in encounter_doc.procedure_prescription:
            if row.procedure == doc.procedure_template:
                frappe.db.set_value(row.doctype, row.name, {
                    "clinical_procedure": doc.name,
                    "delivered_quantity": 1
                })