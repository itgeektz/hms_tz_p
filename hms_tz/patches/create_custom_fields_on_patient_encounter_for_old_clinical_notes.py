import frappe
from frappe.custom.doctype.custom_field.custom_field import create_custom_fields


def execute():
    fields = {
        "Patient Encounter": [
            dict(
                fieldname="hms_tz_previous_section_break",
                fieldtype="Section Break",
                label="Previous History of the Symptoms and Examination Details",
                insert_after="system_and_symptoms",
                collapsible=1,
            ),
            dict(
                fieldname="hms_tz_previous_examination_detail",
                fieldtype="Text Editor",
                label="",
                insert_after="hms_tz_previous_section_break",
                read_only=1,
                transilatable=1,
            ),
            dict(
                fieldname="hms_tz_examination_detail_section_break",
                fieldtype="Section Break",
                label="",
                insert_after="hms_tz_previous_examination_detail",
            ),
            dict(
                fieldname="clear_history",
                fieldtype="Button",
                label="Clear History",
                insert_after="examination_detail",
                hidden=1,
            ),
        ]
    }

    create_custom_fields(fields, update=True)
