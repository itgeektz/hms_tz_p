import frappe
from frappe.custom.doctype.custom_field.custom_field import create_custom_fields


def execute():
    fields = {
        "Company": [
            {
                "fieldname": "allow_discharge_patient_with_pending_unbilled_invoices",
                "label": "Allow Discharge Patient With Pending Unbilled Invoices",
                "fieldtype": "Check",
                "insert_after": "hms_tz_settings_sb",
                "description": "If ticked, Cash patient can be discharged even if there are unbilled invoices",
            }
        ]
    }

    create_custom_fields(fields, update=True)
