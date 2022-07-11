import frappe
from hms_tz.nhif.api.patient_encounter import set_amounts

def execute():
    patient_encounters = frappe.get_all("Patient Encounter", filters={
        "insurance_subscription": ["!=", ""], "docstatus": 1
    }, fields=["name"], pluck="name", order_by="encounter_date")

    for encounter in patient_encounters:
        try:
            doc = frappe.get_doc("Patient Encounter", encounter)
            set_amounts(doc)
            doc.db_update()
        except Exception:
            frappe.log_error(frappe.get_traceback(), str("Set Amount on Encounter via Patch"))
            continue