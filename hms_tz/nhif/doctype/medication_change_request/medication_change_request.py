# -*- coding: utf-8 -*-
# Copyright (c) 2021, Aakvatech and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe import _
from frappe.model.document import Document
from hms_tz.nhif.api.healthcare_utils import (
    get_item_rate,
    get_warehouse_from_service_unit,
    get_template_company_option,
    msgThrow,
)
from hms_tz.hms_tz.doctype.patient_encounter.patient_encounter import get_quantity
from hms_tz.nhif.api.patient_encounter import validate_stock_item
from hms_tz.nhif.api.patient_appointment import get_mop_amount, get_discount_percent
from frappe.model.workflow import apply_workflow
from frappe.utils import get_url_to_form
from hms_tz.nhif.api.patient_encounter import get_drug_quantity

class MedicationChangeRequest(Document):
    def validate(self):
        self.title = "{0}/{1}".format(self.patient_encounter, self.delivery_note)
        self.warehouse = self.get_warehouse_per_delivery_note()
        items = []
        if self.drug_prescription:
            for drug in self.drug_prescription:
                validate_healthcare_service_unit(self.warehouse, drug, method="validate")        
                
                if drug.drug_code not in items:
                    items.append(drug.drug_code)
                else:
                    frappe.throw(_("Drug '{0}' is duplicated in line '{1}' in Drug Prescription").format(
                            frappe.bold(drug.drug_code), frappe.bold(drug.idx)
                        ))

                if not drug.quantity:
                    frappe.throw("Please keep quantity for item: {0}, Row#: {1}".format(
                        frappe.bold(drug.drug_code), frappe.bold(drug.idx)
                    ))
                drug.delivered_quantity = drug.quantity - (drug.quantity_returned or 0)

                template_doc = get_template_company_option(drug.drug_code, self.company)
                drug.is_not_available_inhouse = template_doc.is_not_available
                if drug.is_not_available_inhouse == 1:
                    frappe.msgprint(
                        "NOTE: This healthcare service item, <b>"
                        + drug.drug_code
                        + "</b>, is not available inhouse".format(
                            frappe.bold(drug.drug_code)
                    ))
                
                # auto calculating quantity
                if not drug.quantity:
                    drug.quantity = get_drug_quantity(drug)
                
                validate_stock_item(drug.drug_code, drug.quantity, self.company, drug.doctype, drug.healthcare_service_unit, caller="unknown", method="validate")
                
                self.validate_item_insurance_coverage(drug, "validate")

    @frappe.whitelist()
    def get_warehouse_per_delivery_note(self):
        return frappe.get_value("Delivery Note", self.delivery_note, "set_warehouse")


    def validate_item_insurance_coverage(self, row, method):
        """Validate if the Item is covered with the insurance coverage plan of a patient"""
        if row.prescribe:
            return
        
        insurance_subscription, insurance_company, mop = get_insurance_details(self)
        if mop:
            return
        
        insurance_coverage_plan = frappe.get_cached_value(
            "Healthcare Insurance Subscription",
            {"name": insurance_subscription},
            "healthcare_insurance_coverage_plan"
        )
        if not insurance_coverage_plan:
            frappe.throw(_("Healthcare Insurance Coverage Plan is Not defiend"))
        
        coverage_plan_name, is_exclusions = frappe.get_cached_value(
            "Healthcare Insurance Coverage Plan",
            insurance_coverage_plan,
            ["coverage_plan_name", "is_exclusions"],
        )
        
        today = frappe.utils.nowdate()
        service_coverage = frappe.get_all("Healthcare Service Insurance Coverage",
            filters={"is_active": 1, "start_date": ["<=", today],"end_date": [">=", today],
                "healthcare_service_template": row.drug_code, 
                "healthcare_insurance_coverage_plan": insurance_coverage_plan,
            }, fields=["name", "approval_mandatory_for_claim", "healthcare_service_template"],
        )
        if service_coverage:
            row.is_restricted = service_coverage[0].approval_mandatory_for_claim

            if is_exclusions:
                msgThrow(_(
                        "{0} not covered in Healthcare Insurance Coverage Plan "
                        + str(frappe.bold(coverage_plan_name))
                    ).format(frappe.bold(row.drug_code)),
                    method
                )
            
        else:
            if not is_exclusions:
                msgThrow(_(
                        "{0} not covered in Healthcare Insurance Coverage Plan "
                        + str(frappe.bold(coverage_plan_name))
                    ).format(frappe.bold(row.drug_code)),
                    method
                )



    def before_insert(self):
        if self.patient_encounter:
            encounter_doc = get_patient_encounter_doc(self.patient_encounter)
            if not encounter_doc.insurance_coverage_plan and not encounter_doc.inpatient_record:
                frappe.throw(frappe.bold("Cannot create medication change request for Cash Patient OPD"))
            
            self.warehouse = self.get_warehouse_per_delivery_note()

            for row in encounter_doc.drug_prescription:
                if self.warehouse == get_warehouse_from_service_unit(
                    row.healthcare_service_unit
                ):
                    new_row = row.as_dict()
                    new_row["name"] = None
                    self.append('original_pharmacy_prescription', new_row)
                    self.append('drug_prescription', new_row)
            
            if not self.patient_encounter_final_diagnosis:
                for d in encounter_doc.patient_encounter_final_diagnosis:
                    if not isinstance(d, dict):
                        d = d.as_dict()

                    d["name"] = None

                    self.append("patient_encounter_final_diagnosis", d)
            
            dn_doc = frappe.get_doc("Delivery Note", self.delivery_note)
            
            if dn_doc.form_sales_invoice:
                url = get_url_to_form("sales Ivoice", dn_doc.form_sales_invoice)
                frappe.throw("Cannot create medicaton change request for items paid in cash<br>\
                    refer sales invoice: <a href='{0}'>{1}</a>".format(
                        url, frappe.bold(dn_doc.form_sales_invoice)
                    ))
            
            try:
                if dn_doc.workflow_state != "Changes Requested":
                    apply_workflow(dn_doc, "Request Changes")
                    dn_doc.reload()
                    
            except Exception:
                frappe.log_error(frappe.get_traceback(), str(self.doctype))
                frappe.msgprint("Apply workflow error for delivery note: {0}".format(frappe.bold(dn_doc.name)))
                frappe.throw("Medication Change Request was not created, try again")
    

    def before_submit(self):
        self.warehouse = self.get_warehouse_per_delivery_note()
        for item in self.drug_prescription:
            validate_healthcare_service_unit(self.warehouse, item, method="throw")
            self.validate_item_insurance_coverage(item, "throw")
            set_amount(self, item)
    
    def on_submit(self):
        encounter_doc = self.update_encounter()
        self.update_delivery_note(encounter_doc)

    def update_encounter(self):
        doc = frappe.get_doc("Patient Encounter", self.patient_encounter)
        for line in self.original_pharmacy_prescription:
            for row in doc.drug_prescription:
                if (
                    line.drug_code == row.drug_code
                    and line.healthcare_service_unit == row.healthcare_service_unit
                ):
                    frappe.delete_doc(
                        row.doctype,
                        row.name,
                        force=1,
                        ignore_permissions=True,
                        for_reload=True,
                    )
        doc.reload()
        fields_to_clear = [
            "name",
            "owner",
            "creation",
            "modified",
            "modified_by",
            "docstatus",
            "amended_from",
            "amendment_date",
            "parentfield",
            "parenttype",
        ]
        for row in self.drug_prescription:
            if row.is_not_available_inhouse == 1:
                continue
            new_row = frappe.copy_doc(row).as_dict()
            for fieldname in fields_to_clear:
                new_row[fieldname] = None
            new_row["drug_prescription_created"] = 1
            doc.append("drug_prescription", new_row)
        doc.db_update_all()
        frappe.msgprint(
            _("Patient Encounter " + self.patient_encounter + " has been updated!"),
            alert=True,
        )
        return doc

    def update_delivery_note(self, encounter_doc):
        doc = frappe.get_doc("Delivery Note", self.delivery_note)
        doc.items = []
        doc.hms_tz_original_items = []

        for row in encounter_doc.drug_prescription:
            warehouse = get_warehouse_from_service_unit(row.healthcare_service_unit)
            if warehouse != doc.set_warehouse:
                continue
            
            if row.prescribe and not encounter_doc.inpatient_record:
                continue
            
            if row.is_not_available_inhouse or row.is_cancelled:
                continue

            item_code, uom = frappe.get_cached_value("Medication", row.drug_code, ["item", "stock_uom"])
            is_stock, item_name = frappe.get_cached_value(
                "Item", item_code, ["is_stock_item", "item_name"]
            )
            if not is_stock:
                continue
            item = frappe.new_doc("Delivery Note Item")
            item.item_code = item_code
            item.item_name = item_name
            item.warehouse = warehouse
            item.qty = row.delivered_quantity or 1
            item.medical_code = row.medical_code
            item.rate = row.amount
            item.amount = row.amount * row.delivered_quantity
            item.reference_doctype = row.doctype
            item.reference_name = row.name
            item.is_restricted = row.is_restricted
            item.discount_percentage = row.hms_tz_is_discount_percent
            item.hms_tz_is_discount_applied = row.hms_tz_is_discount_applied
            item.description = (
                row.drug_name
                + " for "
                + (row.dosage or "No Prescription Dosage")
                + " for "
                + (row.period or "No Prescription Period")
                + " with "
                + row.medical_code
                + " and doctor notes: "
                + (row.comment or "Take medication as per dosage.")
            )
            doc.append("items", item)

            new_original_item = set_original_items(doc.name, item)
            new_original_item.stock_uom = uom
            new_original_item.uom = uom
            doc.append("hms_tz_original_items", new_original_item)

        doc.save(ignore_permissions=True)
        doc.reload()

        try:
            if doc.workflow_state != "Changes Made":
                apply_workflow(doc, "Make Changes")
                doc.reload()

                if doc.workflow_state == "Changes Made":
                    frappe.msgprint(
                        _("Delivery Note " + self.delivery_note + " has been updated!"), alert=True
                    )

        except Exception:
            frappe.log_error(frappe.get_traceback(), str("Apply workflow error for delivery note: {0}".format(frappe.bold(doc.name))))
            frappe.throw("Apply workflow error for delivery note: {0}".format(frappe.bold(doc.name)))


@frappe.whitelist()
def get_delivery_note(patient, patient_encounter):
    d_list = frappe.get_all(
        "Delivery Note",
        filters={"reference_name": patient_encounter, "docstatus": 0},
        fields=["name", "set_warehouse"],
    )
    if len(d_list) > 1:
        frappe.throw(
            "There is {0} delivery note of IPD and OPD warehouses, for patient: {1}, and encounter: {2}, \
            Please choose one delivery note between {3} and {4}".format(
                frappe.bold(len(d_list)),
                frappe.bold(patient),
                frappe.bold(patient_encounter),
                frappe.bold(d_list[0].name + ": warehouse: " + d_list[0].set_warehouse),
                frappe.bold(d_list[1].name + ": warehouse: " + d_list[1].set_warehouse),
            )
        )

    if len(d_list) == 1:
        return d_list[0].name
    if len(d_list) == 0:
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


def get_insurance_details(self):
    insurance_subscription, insurance_company, mop = frappe.get_value(
        "Patient Appointment", self.appointment,
        ["insurance_subscription", "insurance_company", "mode_of_payment"],
    )
    return insurance_subscription, insurance_company, mop

def set_amount(self, row):
    item_code = frappe.get_cached_value("Medication", row.drug_code, "item")
    inpatient_record = frappe.get_value("Patient", self.patient, "inpatient_record")
    insurance_subscription, insurance_company, mop = get_insurance_details(self)

    # apply discount if it is available on Heathcare Insurance Company
    discount_percent = 0
    if insurance_company and "NHIF" not in insurance_company:
        discount_percent = get_discount_percent(insurance_company)

    if insurance_subscription and not row.prescribe:
        amount = get_item_rate(
            item_code, self.company, insurance_subscription, insurance_company
        )
        row.amount = amount - (amount * (discount_percent/100))
        if discount_percent > 0:
            row.hms_tz_is_discount_applied = 1
            row.hms_tz_is_discount_percent = discount_percent

    elif mop and inpatient_record:
        if not row.prescribe:
            row.prescribe = 1
        row.amount = get_mop_amount(item_code, mop, self.company,self.patient)


@frappe.whitelist()
def validate_healthcare_service_unit(warehouse, item, method):
    if warehouse != get_warehouse_from_service_unit(item.healthcare_service_unit):
        msgThrow(
            _(
                "Please change healthcare service unit: {0}, for drug: {1} row: {2}\
                as it is of different warehouse".format(
                    frappe.bold(item.healthcare_service_unit),
                    frappe.bold(item.drug_code),
                    frappe.bold(item.idx),
                )
            ),
            method,
        )


@frappe.whitelist()
def get_items_on_change_of_delivery_note(name, encounter, delivery_note):
    doc = frappe.get_doc("Medication Change Request", name)

    if not doc or not encounter or not delivery_note:
        return

    patient_encounter_doc = get_patient_encounter_doc(encounter)
    delivery_note_doc = frappe.get_doc("Delivery Note", delivery_note)

    doc.original_pharmacy_prescription = []
    doc.drug_prescription = []
    for item_line in patient_encounter_doc.drug_prescription:
        if delivery_note_doc.set_warehouse != get_warehouse_from_service_unit(
            item_line.healthcare_service_unit
        ):
            continue
        row = item_line.as_dict()
        row["name"] = None
        row["parent"] = None
        row["parentfield"] = None
        row["parenttype"] = None
        doc.append("original_pharmacy_prescription", row)
        doc.append("drug_prescription", row)
    doc.delivery_note = delivery_note
    doc.save(ignore_permissions=True)
    doc.reload()
    return doc


def get_fields_to_clear():
    return ["name", "owner", "creation", "modified", "modified_by", "docstatus"]


def set_original_items(name, item):
    new_row = item.as_dict()
    for fieldname in get_fields_to_clear():
        new_row[fieldname] = None        
    
    new_row.update({
        "parent": name,
        "parentfield": "hms_tz_original_items",
        "parenttype": "Delivery Note",
        "doctype": "Original Delivery Note Item"
    })
    
    return new_row


@frappe.whitelist()
def create_medication_change_request_from_dn(doctype, name):
    source_doc = frappe.get_doc(doctype, name)
    
    if source_doc.form_sales_invoice:
        url = get_url_to_form("sales Ivoice", source_doc.form_sales_invoice)
        frappe.throw("Cannot create medicaton change request for items paid in cash,<br>\
            please refer sales invoice: <a href='{0}'>{1}</a>".format(
                url, frappe.bold(source_doc.form_sales_invoice)
            ))
    
    if not source_doc.hms_tz_comment:
        frappe.throw("<b>No comment found on the delivery note, Please keep a comment and save the delivery note, before creating med change request</b>")

    doc = frappe.new_doc("Medication Change Request")
    doc.patient = source_doc.patient
    doc.patient_name = source_doc.patient_name
    doc.appointment = source_doc.hms_tz_appointment_no
    doc.company = source_doc.company
    doc.patient_encounter = source_doc.reference_name
    doc.delivery_note = source_doc.name
    doc.healthcare_practitioner = source_doc.healthcare_practitioner
    doc.hms_tz_comment = source_doc.hms_tz_comment

    doc.save(ignore_permissions=True)
    url = get_url_to_form(doc.doctype, doc.name)
    frappe.msgprint("Draft Medication Change Request: <a href='{0}'>{1}</a> is created".format(
        url, frappe.bold(doc.name)
    ))
    return doc.name

