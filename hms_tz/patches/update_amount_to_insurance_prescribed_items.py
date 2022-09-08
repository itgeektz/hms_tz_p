import frappe
from frappe import _
from hms_tz.nhif.api.patient_appointment import get_mop_amount


def execute():
    patient_encounters = frappe.get_all(
        "Patient Encounter",
        filters={
            "insurance_subscription": ["!=", ""],
            "encounter_date": [">=", "2022-05-01"],
            "docstatus": 1,
        },
        fields=["name"],
        pluck="name",
        order_by="encounter_date",
    )

    if not patient_encounters:
        return

    for encounter in patient_encounters:
        doc = frappe.get_doc("Patient Encounter", encounter)

        for child in get_child_maps():
            for row in doc.get(child.get("table")):
                if row.amount:
                    continue

                try:
                    item_rate = 0
                    item_code = frappe.get_value(
                        child.get("doctype"), row.get(child.get("item")), "item"
                    )

                    if row.prescribe and doc.insurance_subscription:
                        item_rate = get_mop_amount(
                            item_code, "Cash", doc.company, doc.patient
                        )
                        if not item_rate or item_rate == 0:
                            frappe.throw(
                                _(
                                    "Cannot get mode of payment rate for item {0}"
                                ).format(item_code)
                            )

                    frappe.db.set_value(row.doctype, row.name, "amount", item_rate)

                except Exception:
                    frappe.log_error(
                        frappe.get_traceback(), str("Set Amount on Encounter via Patch")
                    )


def get_child_maps():

    return [
        {
            "table": "lab_test_prescription",
            "doctype": "Lab Test Template",
            "item": "lab_test_code",
        },
        {
            "table": "radiology_procedure_prescription",
            "doctype": "Radiology Examination Template",
            "item": "radiology_examination_template",
        },
        {
            "table": "procedure_prescription",
            "doctype": "Clinical Procedure Template",
            "item": "procedure",
        },
        {
            "table": "drug_prescription",
            "doctype": "Medication",
            "item": "drug_code",
        },
        {
            "table": "therapies",
            "doctype": "Therapy Type",
            "item": "therapy_type",
        },
    ]
