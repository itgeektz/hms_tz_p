# -*- coding: utf-8 -*-
# Copyright (c) 2021, Aakvatech and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document


class MedicationChangeRequest(Document):
    pass


@frappe.whitelist()
def get_delivery_note(patient_encounter):
    d_list = frappe.get_all("Delivery Note", filters={
        "reference_name": patient_encounter,
        "docstatus": 0
    })
    if len(d_list):
        return d_list[0].name
    else:
        return ""


@frappe.whitelist()
def get_patient_encounter_name(delivery_note):
    doc = frappe.get_doc("Delivery Note", delivery_note)
    if doc.reference_doctype and doc.reference_name:
        if doc.reference_doctype == "Patient Encounter":
            return doc.reference_name
    return ""


@frappe.whitelist()
def get_patient_encounter_doc(patient_encounter):
    doc = frappe.get_doc("Patient Encounter", patient_encounter)
    return doc
