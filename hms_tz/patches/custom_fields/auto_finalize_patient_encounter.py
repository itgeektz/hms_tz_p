import frappe
from frappe.custom.doctype.custom_field.custom_field import create_custom_fields


def execute():
    fields = {
        "Company": [
            {
                "fieldname": "auto_finalize_patient_encounter",
                "label": "Auto Finalize Patient Encounter",
                "fieldtype": "Check",
                "insert_after": "hms_tz_settings_sb",
                "description": "if ticked, patient encounter will be finalized automatically after the number of days set in the field below",
            },
            {
                "fieldname": "valid_days_to_auto_finalize_encounter",
                "label": "valid days to finalize patient encounter",
                "fieldtype": "Int",
                "insert_after": "auto_finalize_patient_encounter",
                "depends_on": "eval:doc.auto_finalize_patient_encounter == 1",
                "description": "Number of days to finalize patient encounter",
                "mandatory_depends_on": "eval:doc.auto_finalize_patient_encounter == 1",
            },
        ]
    }

    create_custom_fields(fields, update=True)
