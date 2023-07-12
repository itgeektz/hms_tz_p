import frappe
from frappe.custom.doctype.custom_field.custom_field import create_custom_fields    

def execute():
    fields = {
        "Company": [
            {
                "fieldname": "validate_medication_class",
                "label": "Validate Medication Class",
                "fieldtype": "Check",
                "insert_after": "hms_tz_limit_exceed_action",
                "description": "If checked, medication class will be validated on patient encounter",
            }
        ]
    }

    create_custom_fields(fields, update=True)