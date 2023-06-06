import frappe
from frappe.custom.doctype.custom_field.custom_field import create_custom_fields

def execute():
    fields = {
        "Company": [
            {
                "fieldname": "auto_set_pharmacy_on_patient_encounter",
                "label": "Auto Set Pharmacy on Patient Encounter",
                "fieldtype": "Check",
                "insert_after": "hms_tz_minimum_cash_limit_percent",
                "description": "If ticked then pharmacy will be auto set on patient encounter, depending on cash, insurance or inpatient",
            },
            {
                "fieldname": "opd_cash_pharmacy",
                "label": "OPD Cash Pharmacy",
                "fieldtype": "Link",
                "options": "Healthcare Service Unit",
                "insert_after": "auto_set_pharmacy_on_patient_encounter",
                "depends_on": "eval:doc.auto_set_pharmacy_on_patient_encounter == 1",
                "mandatory_depends_on": "eval:doc.auto_set_pharmacy_on_patient_encounter == 1",
            },
            {
                "fieldname": "opd_insurance_pharmacy",
                "label": "OPD Insurance Pharmacy",
                "fieldtype": "Link",
                "options": "Healthcare Service Unit",
                "insert_after": "opd_cash_pharmacy",
                "depends_on": "eval:doc.auto_set_pharmacy_on_patient_encounter == 1",
                "mandatory_depends_on": "eval:doc.auto_set_pharmacy_on_patient_encounter == 1",
            },
            {
                "fieldname": "ipd_cash_pharmacy",
                "label": "IPD Cash Pharmacy",
                "fieldtype": "Link",
                "options": "Healthcare Service Unit",
                "insert_after": "opd_insurance_pharmacy",
                "depends_on": "eval: doc.auto_set_pharmacy_on_patient_encounter == 1",
                "mandatory_depends_on": "eval: doc.auto_set_pharmacy_on_patient_encounter == 1",
            },
            {
                "fieldname": "ipd_insurance_pharmacy",
                "label": "IPD Insurance Pharmacy",
                "fieldtype": "Link",
                "options": "Healthcare Service Unit",
                "insert_after": "ipd_cash_pharmacy",
                "depends_on": "eval: doc.auto_set_pharmacy_on_patient_encounter == 1",
                "mandatory_depends_on": "eval: doc.auto_set_pharmacy_on_patient_encounter == 1",
            }
        ],
    }

    create_custom_fields(fields, update=True)