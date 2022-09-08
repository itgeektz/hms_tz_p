import frappe
from hms_tz.hms_tz.doctype.clinical_procedure.clinical_procedure import (
    insert_clinical_procedure_to_medical_record,
)


def execute():
    procedures = frappe.get_all(
        "Clinical Procedure",
        filters={"docstatus": 1},
        fields=["name"],
        order_by="start_date",
        pluck="name",
    )

    if not procedures:
        return

    medical_records = frappe.get_all(
        "Patient Medical Record",
        filters={"reference_doctype": "Clinical Procedure"},
        fields=["reference_name"],
        order_by="communication_date",
        pluck="reference_name",
    )

    for procedure in procedures:
        if procedure not in medical_records:
            doc = frappe.get_doc("Clinical Procedure", procedure)
            insert_clinical_procedure_to_medical_record(doc)

    frappe.db.commit()
