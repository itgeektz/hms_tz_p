# -*- coding: utf-8 -*-
# Copyright (c) 2021, Aakvatech and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document
from hms_tz.nhif.api.healthcare_utils import get_item_rate, get_warehouse_from_service_unit
from hms_tz.hms_tz.doctype.patient_encounter.patient_encounter import get_quantity

class MedicationChangeRequest(Document):
    def validate(self):
        self.title = "{0}/{1}".format(self.patient_encounter,
                                      self.delivery_note)
        if self.drug_prescription:
            for drug in self.drug_prescription:
                if not drug.quantity or drug.quantity == 0:
                    drug.quantity = get_quantity(drug)

    def on_submit(self):
        self.update_encounter()
        self.update_delivery_note()

    def update_encounter(self):
        doc = frappe.get_doc("Patient Encounter", self.patient_encounter)
        for row in doc.drug_prescription:
            frappe.delete_doc(row.doctype, row.name, force=1,
                              ignore_permissions=True, for_reload=True)
        frappe.db.commit()
        doc.reload()
        fields_to_clear = ['name', 'owner', 'creation', 'modified', 'modified_by',
                           'docstatus', 'amended_from', 'amendment_date', 'parentfield', 'parenttype']
        for row in self.drug_prescription:
            new_row = frappe.copy_doc(row).as_dict()
            for fieldname in (fields_to_clear):
                new_row[fieldname] = None
            doc.append('drug_prescription', new_row)
        doc.db_update_all()
        frappe.db.commit()
        frappe.msgprint(_("Patient Encounter " + self.patient_encounter + " has been updated!"), alert=True)

    def update_delivery_note(self):
        doc = frappe.get_doc("Delivery Note", self.delivery_note)
        doc.items = []
        insurance_subscription, insurance_company, service_unit = frappe.get_value(
            "Patient Appointment", self.appointment, ["insurance_subscription", "insurance_company", "service_unit"])
        warehouse = get_warehouse_from_service_unit(
            service_unit)
        for row in self.drug_prescription:
            if row.prescribe:
                continue
            item_code = frappe.get_value(
                "Medication", row.drug_code, "item_code")
            is_stock, item_name = frappe.get_value(
                "Item", item_code, ["is_stock_item", "item_name"])
            if not is_stock:
                continue
            item = frappe.new_doc("Delivery Note Item")
            item.item_code = item_code
            item.item_name = item_name
            item.warehouse = warehouse
            item.qty = row.quantity or 1
            item.medical_code = row.medical_code
            item.rate = get_item_rate(
                item_code, self.company, insurance_subscription, insurance_company)
            item.reference_doctype = row.doctype
            item.reference_name = row.name
            item.description = row.drug_name + " for " + row.dosage + " for " + \
                row.period + " with specific notes as follows: " + \
                (row.comment or "No Comments")
            doc.append('items', item)
        doc.save(ignore_permissions=True)
        frappe.msgprint(_("Patient Encounter " + self.delivery_note + " has been updated!"), alert=True)


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

