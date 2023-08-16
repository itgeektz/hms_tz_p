import frappe
from frappe.custom.doctype.custom_field.custom_field import create_custom_fields


def execute():
    fields = {
        "Appointment Type": [
            {
                "fieldname": "has_no_consultation_charges",
                "fieldtype": "Check",
                "label": "Has No Consultation Charge",
                "insert_after": "visit_type_id",
                "description": "If checked, Consultation Charges will not be applied for appointments of NHIF Patients",
            }
        ],
        "Patient Appointment": [
            {
                "fieldname": "has_no_consultation_charges",
                "fieldtype": "Check",
                "label": "Has No Consultation Charge",
                "insert_after": "follow_up",
                "read_only": 1,
                "description": "If checked, Consultation Charges will not be applied for appointments of NHIF Patients",
            }
        ],
    }

    create_custom_fields(fields, update=True)
