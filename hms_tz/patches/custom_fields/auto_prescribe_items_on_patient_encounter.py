import frappe
from frappe.custom.doctype.custom_field.custom_field import create_custom_fields

def execute():
    fields = {
        "Company": [
            {
                "fieldname": "auto_prescribe_items_on_patient_encounter",
                "label": "Auto Prescribe Items on Patient Encounter",
                "fieldtype": "Check",
                "insert_after": "hms_tz_settings_sb",
                "default": 1,
                "description": "If ticked, Uncovered items will be marked as prescribed and required to be paid in cash on patient encounter"
            }
        ]
    }

    create_custom_fields(fields, update=True)