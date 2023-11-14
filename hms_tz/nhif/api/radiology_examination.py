# -*- coding: utf-8 -*-
# Copyright (c) 2020, Aakvatech and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe import _
from hms_tz.nhif.api.healthcare_utils import create_delivery_note_from_LRPT
from hms_tz.nhif.api.healthcare_utils import get_restricted_LRPT
from frappe.utils import getdate, get_fullname, nowdate


def validate(doc, method):
    if not doc.prescribe:
        is_restricted = get_restricted_LRPT(doc)
        doc.is_restricted = is_restricted


def before_submit(doc, method):
    if doc.is_restricted and not doc.approval_number:
        frappe.throw(
            _(
                f"Approval number is required for <b>{doc.radiology_examination_template}</b>. Please set the Approval Number."
            )
        )

    doc.hms_tz_submitted_by = get_fullname(frappe.session.user)
    doc.hms_tz_user_id = frappe.session.user
    doc.hms_tz_submitted_date = nowdate()

    # 2023-07-13
    # stop this validation for now
    return
    if doc.approval_number and doc.approval_status != "Verified":
        frappe.throw(
            _(
                f"Approval number: <b>{doc.approval_number}</b> for item: <b>{doc.radiology_examination_template}</b> is not verified.>br>\
                    Please verify the Approval Number."
            )
        )


def on_submit(doc, method):
    update_radiology_procedure_prescription(doc)
    create_delivery_note(doc)


def on_cancel(doc, method):
    doc.flags.ignore_links = True

    if doc.docstatus == 2:
        frappe.db.set_value(
            "Radiology Procedure Prescription",
            doc.hms_tz_ref_childname,
            "radiology_examination",
            "",
        )

        new_radiology_doc = frappe.copy_doc(doc)
        new_radiology_doc.workflow_state = None
        new_radiology_doc.amended_from = doc.name
        new_radiology_doc.save(ignore_permissions=True)

        url = frappe.utils.get_url_to_form(
            new_radiology_doc.doctype, new_radiology_doc.name
        )
        frappe.msgprint(
            f"Radiology Examination: <strong>{doc.name}</strong> is cancelled:<br>\
            New Radiology Examination: <a href='{url}'><strong>{new_radiology_doc.name}</strong></a> is successful created"
        )


def create_delivery_note(doc):
    if doc.ref_doctype and doc.ref_docname and doc.ref_doctype == "Patient Encounter":
        patient_encounter_doc = frappe.get_doc(doc.ref_doctype, doc.ref_docname)
        create_delivery_note_from_LRPT(doc, patient_encounter_doc)


def update_radiology_procedure_prescription(doc):
    if doc.ref_doctype == "Patient Encounter":
        encounter_doc = frappe.get_doc(doc.ref_doctype, doc.ref_docname)
        for row in encounter_doc.radiology_procedure_prescription:
            if (
                row.name == doc.hms_tz_ref_childname
                and row.radiology_examination_template
                == doc.radiology_examination_template
            ):
                frappe.db.set_value(
                    row.doctype,
                    row.name,
                    {"radiology_examination": doc.name, "delivered_quantity": 1},
                )
