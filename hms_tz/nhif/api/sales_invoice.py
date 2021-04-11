# -*- coding: utf-8 -*-
# Copyright (c) 2020, Aakvatech and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe import _
from hms_tz.nhif.api.healthcare_utils import (
    update_dimensions,
    create_individual_lab_test,
    create_individual_radiology_examination,
    create_individual_procedure_prescription,
)


def validate(doc, method):
    for item in doc.items:
        if not item.is_free_item and item.amount == 0:
            frappe.throw(
                _(
                    "Amount of the healthcare service <b>'{0}'</b> cannot be ZERO. Please do not select this item and request Pricing team to resolve this."
                ).format(item.item_name)
            )
    update_dimensions(doc)


@frappe.whitelist()
def create_pending_healthcare_docs(doc_name):
    doc = frappe.get_doc("Sales Invoice", doc_name)
    create_healthcare_docs(doc, "From Front End")


def before_submit(doc, method):
    frappe.throw(str(doc.outstanding_amount))
    if doc.is_pos and doc.outstanding_amount != 0:
        frappe.throw(
            _(
                "Sales invoice not paid in full. Make sure that full paid amount is entered in Mode of Payments table."
            )
        )


def on_submit(doc, method):
    create_healthcare_docs(doc, method)


def create_healthcare_docs(doc, method):
    if doc.docstatus != 1:
        return
    for item in doc.items:
        if item.reference_dt:
            if item.reference_dt == "Healthcare Service Order":
                hso_doc = frappe.get_doc("Healthcare Service Order", item.reference_dn)
                if hso_doc.insurance_subscription and not hso_doc.prescribed:
                    return
                if not hso_doc.order:
                    frappe.msgprint(_("HSO order not found..."), alert=True)
                    return
                child = frappe.get_doc(
                    hso_doc.order_reference_doctype, hso_doc.order_reference_name
                )
                if hso_doc.order_doctype == "Lab Test Template":
                    create_individual_lab_test(hso_doc, child)
                elif hso_doc.order_doctype == "Radiology Examination Template":
                    create_individual_radiology_examination(hso_doc, child)
                elif hso_doc.order_doctype == "Clinical Procedure Template":
                    create_individual_procedure_prescription(hso_doc, child)
