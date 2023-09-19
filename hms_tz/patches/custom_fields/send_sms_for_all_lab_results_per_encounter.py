import frappe
from frappe.custom.doctype.custom_field.custom_field import create_custom_fields


def execute():
    fields = {
        "Company": [
            {
                "fieldname": "allow_send_sms_for_multiple_labs",
                "label": "Allow Send SMS for Multiple Labs",
                "fieldtype": "Check",
                "insert_after": "hms_tz_settings_sb",
                "description": "Allow sending SMS for all lab results per single encounter",
            },
            {
                "fieldname": "lab_result_sms_template",
                "label": "Lab Result SMS Template",
                "fieldtype": "Small Text",
                "insert_after": "allow_send_sms_for_multiple_labs",
                "description": "This sms SMS template will be a message sent to patient",
                "depends_on": "eval:doc.allow_send_sms_for_multiple_labs == 1",
                "mandatory_depends_on": "eval:doc.allow_send_sms_for_multiple_labs == 1",
                "default": "Dear {{doc.patient_name}}, your lab results are ready. Please visit the hospital to collect them.",
            },
        ]
    }
    create_custom_fields(fields, update=True)
