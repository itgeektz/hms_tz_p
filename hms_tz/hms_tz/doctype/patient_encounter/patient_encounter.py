# -*- coding: utf-8 -*-
# Copyright (c) 2015, ESS LLP and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
import json
from frappe import _
from frappe.model.document import Document
from frappe.utils import cstr
from frappe import _
from hms_tz.hms_tz.utils import make_healthcare_service_order


class PatientEncounter(Document):
    def validate(self):
        self.set_title()
        if self.drug_prescription:
            for drug in self.drug_prescription:
                if not drug.quantity or drug.quantity == 0:
                    # Remarked by MPC_TZ 2022-06-10 16:16 to avoid automatic qty calculations
                    # drug.quantity = get_quantity(drug)
                    drug.quantity = 0

    def on_update(self):
        if self.appointment:
            frappe.db.set_value(
                "Patient Appointment", self.appointment, "status", "Closed"
            )
        update_encounter_medical_record(self)

    def after_insert(self):
        insert_encounter_to_medical_record(self)

    def on_submit(self):
        update_encounter_medical_record(self)
        create_therapy_plan(self)
        # create_healthcare_service_order(self)
        # make_insurance_claim(self)

    def on_cancel(self):
        if self.appointment:
            frappe.db.set_value(
                "Patient Appointment", self.appointment, "status", "Open"
            )
        delete_medical_record(self)

    def set_title(self):
        self.title = _("{0} with {1}").format(
            self.patient_name or self.patient,
            self.practitioner_name or self.practitioner,
        )[:100]


def create_therapy_plan(encounter):
    if len(encounter.therapies):
        therapies = []
        for row in encounter.therapies:
            if (
                row.is_cancelled
                or row.hms_tz_is_limit_exceeded
                or row.is_not_available_inhouse
            ):
                continue

            therapies.append(row)
        if len(therapies) == 0:
            return

        doc = frappe.new_doc("Therapy Plan")
        doc.patient = encounter.patient
        doc.company = encounter.company
        doc.start_date = encounter.encounter_date
        doc.hms_tz_appointment = encounter.appointment
        doc.hms_tz_patient_age = encounter.patient_age
        doc.hms_tz_patient_sex = encounter.patient_sex
        doc.hms_tz_insurance_coverage_plan = encounter.insurance_coverage_plan
        doc.ref_doctype = "Patient Encounter"
        doc.ref_docname = encounter.name
        for entry in therapies:
            doc.append(
                "therapy_plan_details",
                {
                    "therapy_type": entry.therapy_type,
                    "no_of_sessions": entry.no_of_sessions,
                    "prescribe": entry.prescribe or 0,
                },
            )
        doc.save(ignore_permissions=True)
        if doc.get("name"):
            encounter.db_set("therapy_plan", doc.name)
            frappe.msgprint(
                _("Therapy Plan {0} created successfully.").format(
                    frappe.bold(doc.name)
                ),
                alert=True,
            )


def insert_encounter_to_medical_record(doc):
    subject = set_subject_field(doc)
    medical_record = frappe.new_doc("Patient Medical Record")
    medical_record.patient = doc.patient
    medical_record.subject = subject
    medical_record.status = "Open"
    medical_record.communication_date = doc.encounter_date
    medical_record.reference_doctype = "Patient Encounter"
    medical_record.reference_name = doc.name
    medical_record.reference_owner = doc.owner
    medical_record.save(ignore_permissions=True)


def update_encounter_medical_record(encounter):
    medical_record_id = frappe.db.exists(
        "Patient Medical Record", {"reference_name": encounter.name}
    )

    if medical_record_id and medical_record_id[0][0]:
        subject = set_subject_field(encounter)
        frappe.db.set_value(
            "Patient Medical Record", medical_record_id[0][0], "subject", subject
        )
    else:
        insert_encounter_to_medical_record(encounter)


def delete_medical_record(encounter):
    frappe.delete_doc_if_exists(
        "Patient Medical Record", "reference_name", encounter.name
    )


def set_subject_field(encounter):
    subject = (
        frappe.bold(_("Healthcare Practitioner: ")) + encounter.practitioner + "<br>"
    )
    if encounter.symptoms:
        subject += frappe.bold(_("Symptoms: ")) + "<br>"
        for entry in encounter.symptoms:
            subject += cstr(entry.complaint) + "<br>"
    else:
        subject += frappe.bold(_("No Symptoms")) + "<br>"

    if encounter.diagnosis:
        subject += frappe.bold(_("Diagnosis: ")) + "<br>"
        for entry in encounter.diagnosis:
            subject += cstr(entry.diagnosis) + "<br>"
    else:
        subject += frappe.bold(_("No Diagnosis")) + "<br>"

    if encounter.drug_prescription:
        subject += "<br>" + _("Drug(s) Prescribed.")
    if encounter.lab_test_prescription:
        subject += "<br>" + _("Test(s) Prescribed.")
    if encounter.procedure_prescription:
        subject += "<br>" + _("Procedure(s) Prescribed.")
    if encounter.therapies:
        subject += "<br>" + _("Therapy Prescribed.")
    if encounter.radiology_procedure_prescription:
        subject += "<br>" + _("Radiology Procedure(s) Prescribed.")

    return subject


def create_healthcare_service_order(encounter):
    if encounter.drug_prescription:
        for drug in encounter.drug_prescription:
            medication = frappe.get_doc("Medication", drug.drug_code)
            args = {
                "healthcare_service_order_category": medication.get_value(
                    "healthcare_service_order_category"
                ),
                "patient_care_type": medication.get_value("patient_care_type"),
                "order_date": encounter.get_value("encounter_date"),
                "ordered_by": encounter.get_value("practitioner"),
                "order_group": encounter.name,
                "replaces": drug.get_value("replaces"),
                "patient": encounter.get_value("patient"),
                "order_doctype": "Medication",
                "order": medication.name,
                "order_description": medication.get_value("description"),
                "intent": drug.get_value("intent"),
                "priority": drug.get_value("priority"),
                "quantity": drug.get_value("quantity"),
                "sequence": drug.get_value("sequence"),
                "expected_date": drug.get_value("expected_date"),
                "as_needed": drug.get_value("as_needed"),
                "occurrence": drug.get_value("occurrence"),
                "staff_role": medication.get_value("staff_role"),
                "note": drug.get_value("note"),
                "patient_instruction": drug.get_value("patient_instruction"),
                "company": encounter.company,
                "insurance_subscription": encounter.insurance_subscription
                if encounter.insurance_subscription
                else "",
                "order_reference_doctype": "Drug Prescription",
                "order_reference_name": drug.name,
            }
            make_healthcare_service_order(args)
    if encounter.lab_test_prescription:
        for labtest in encounter.lab_test_prescription:
            lab_template = frappe.get_doc("Lab Test Template", labtest.lab_test_code)
            args = {
                "healthcare_service_order_category": lab_template.get_value(
                    "healthcare_service_order_category"
                ),
                "patient_care_type": lab_template.get_value("patient_care_type"),
                "order_date": encounter.get_value("encounter_date"),
                "ordered_by": encounter.get_value("practitioner"),
                "order_group": encounter.name,
                "replaces": labtest.get_value("replaces"),
                "patient": encounter.get_value("patient"),
                "order_doctype": "Lab Test Template",
                "order": lab_template.name,
                "order_description": lab_template.get_value("lab_test_description"),
                "quantity": 1,
                "intent": labtest.get_value("intent"),
                "priority": labtest.get_value("priority"),
                "sequence": labtest.get_value("sequence"),
                "as_needed": labtest.get_value("as_needed"),
                "staff_role": lab_template.get_value("staff_role"),
                "note": labtest.get_value("note"),
                "patient_instruction": labtest.get_value("patient_instruction"),
                "healthcare_service_unit_type": lab_template.get_value(
                    "healthcare_service_unit_type"
                ),
                "company": encounter.company,
                "source": encounter.source,
                "referring_practitioner": encounter.referring_practitioner,
                "insurance_subscription": encounter.insurance_subscription
                if encounter.insurance_subscription
                else "",
                "order_reference_doctype": "Lab Prescription",
                "order_reference_name": labtest.name,
            }
            make_healthcare_service_order(args)
    if encounter.procedure_prescription:
        for procedure in encounter.procedure_prescription:
            procedure_template = frappe.get_doc(
                "Clinical Procedure Template", procedure.procedure
            )
            args = {
                "healthcare_service_order_category": procedure_template.get_value(
                    "healthcare_service_order_category"
                ),
                "patient_care_type": procedure_template.get_value("patient_care_type"),
                "order_date": encounter.get_value("encounter_date"),
                "ordered_by": encounter.get_value("practitioner"),
                "order_group": encounter.name,
                "replaces": procedure.get_value("replaces"),
                "patient": encounter.get_value("patient"),
                "order_doctype": "Clinical Procedure Template",
                "order": procedure_template.name,
                "order_description": procedure_template.get_value("description"),
                "quantity": 1,
                "intent": procedure.get_value("intent"),
                "priority": procedure.get_value("priority"),
                "sequence": procedure.get_value("sequence"),
                "as_needed": procedure.get_value("as_needed"),
                "body_part": procedure.get_value("body_part"),
                "staff_role": procedure_template.get_value("staff_role"),
                "note": procedure.get_value("note"),
                "patient_instruction": procedure.get_value("patient_instruction"),
                "healthcare_service_unit_type": procedure_template.get_value(
                    "healthcare_service_unit_type"
                ),
                "company": encounter.company,
                "source": encounter.source,
                "referring_practitioner": encounter.referring_practitioner,
                "insurance_subscription": encounter.insurance_subscription
                if encounter.insurance_subscription
                else "",
                "order_reference_doctype": "Procedure Prescription",
                "order_reference_name": procedure.name,
            }
            make_healthcare_service_order(args)
    if encounter.therapies:
        for therapy in encounter.therapies:
            therapy_type = frappe.get_doc("Therapy Type", therapy.therapy_type)
            args = {
                "healthcare_service_order_category": therapy_type.get_value(
                    "healthcare_service_order_category"
                ),
                "patient_care_type": therapy_type.get_value("patient_care_type"),
                "order_date": encounter.get_value("encounter_date"),
                "ordered_by": encounter.get_value("practitioner"),
                "order_group": encounter.name,
                "replaces": therapy.get_value("replaces"),
                "patient": encounter.get_value("patient"),
                "order_doctype": "Therapy Type",
                "order": therapy_type.name,
                "order_description": therapy_type.get_value("description"),
                "quantity": 1,
                "intent": therapy.get_value("intent"),
                "priority": therapy.get_value("priority"),
                "sequence": therapy.get_value("sequence"),
                "as_needed": therapy.get_value("as_needed"),
                "staff_role": therapy_type.get_value("staff_role"),
                "note": therapy.get_value("note"),
                "patient_instruction": therapy.get_value("patient_instruction"),
                "company": encounter.company,
                "source": encounter.source,
                "referring_practitioner": encounter.referring_practitioner,
                "insurance_subscription": encounter.insurance_subscription
                if encounter.insurance_subscription
                else "",
                "order_reference_doctype": "Therapy Plan Detail",
                "order_reference_name": therapy.name
                # 'healthcare_service_unit_type':therapy_type.get_value('healthcare_service_unit_type')
            }
            make_healthcare_service_order(args)
    if encounter.radiology_procedure_prescription:
        for radiology in encounter.radiology_procedure_prescription:
            radiology_template = frappe.get_doc(
                "Radiology Examination Template",
                radiology.radiology_examination_template,
            )
            args = {
                "healthcare_service_order_category": radiology_template.get_value(
                    "healthcare_service_order_category"
                ),
                "patient_care_type": radiology_template.get_value("patient_care_type"),
                "order_date": encounter.get_value("encounter_date"),
                "ordered_by": encounter.get_value("practitioner"),
                "order_group": encounter.name,
                "replaces": radiology.get_value("replaces"),
                "patient": encounter.get_value("patient"),
                "order_doctype": "Radiology Examination Template",
                "order": radiology_template.name,
                "order_description": radiology_template.get_value("description"),
                "quantity": 1,
                "intent": radiology.get_value("intent"),
                "priority": radiology.get_value("priority"),
                "sequence": radiology.get_value("sequence"),
                "as_needed": radiology.get_value("as_needed"),
                "staff_role": radiology_template.get_value("staff_role"),
                "note": radiology.get_value("note"),
                "patient_instruction": radiology.get_value("patient_instruction"),
                "healthcare_service_unit_type": radiology_template.get_value(
                    "healthcare_service_unit_type"
                ),
                "company": encounter.company,
                "source": encounter.source,
                "referring_practitioner": encounter.referring_practitioner,
                "insurance_subscription": encounter.insurance_subscription
                if encounter.insurance_subscription
                else "",
                "order_reference_doctype": "Radiology Procedure Prescription",
                "order_reference_name": radiology.name,
            }
            make_healthcare_service_order(args)


@frappe.whitelist()
def create_patient_referral(args):
    patient_referral = frappe.new_doc("Patient Referral")
    args = json.loads(args)
    for key in args:
        patient_referral.set(key, args[key] if args[key] else "")
    patient_referral.save(ignore_permissions=True)


def make_insurance_claim(doc):
    return
    if doc.insurance_subscription:
        from hms_tz.hms_tz.utils import (
            create_insurance_claim,
            get_service_item_and_practitioner_charge,
        )

        billing_item, rate = get_service_item_and_practitioner_charge(doc)
        insurance_claim, claim_status = create_insurance_claim(
            doc, "Appointment Type", doc.appointment_type, 1, billing_item
        )
        if insurance_claim:
            frappe.set_value(doc.doctype, doc.name, "insurance_claim", insurance_claim)
            frappe.set_value(doc.doctype, doc.name, "claim_status", claim_status)
            doc.reload()


def get_quantity(self):
    quantity = 0
    dosage = None
    period = None

    if self.dosage:
        dosage = frappe.get_doc("Prescription Dosage", self.dosage)
        for item in dosage.dosage_strength:
            quantity += item.strength
        if self.period and self.interval:
            period = frappe.get_doc("Prescription Duration", self.period)
            if self.interval < period.get_days():
                quantity = quantity * (period.get_days() / self.interval)

    elif self.interval and self.interval_uom and self.period:
        period = frappe.get_doc("Prescription Duration", self.period)
        interval_in = self.interval_uom
        if interval_in == "Day" and self.interval < period.get_days():
            quantity = period.get_days() / self.interval
        elif interval_in == "Hour" and self.interval < period.get_hours():
            quantity = period.get_hours() / self.interval
    if quantity > 0:
        return quantity
    else:
        return 1
