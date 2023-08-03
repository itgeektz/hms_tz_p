import frappe
from frappe.custom.doctype.custom_field.custom_field import create_custom_fields


def execute():
    fields = {
        "Lab Test": [
            {
                "fieldname": "hms_tz_submit_cb",
                "fieldtype": "Column Break",
                "insert_after": "hms_tz_ref_childname",
            },
            {
                "fieldname": "hms_tz_submitted_by",
                "fieldtype": "Data",
                "label": "Submitted By",
                "insert_after": "hms_tz_submit_cb",
                "read_only": 1,
            },
            {
                "fieldname": "hms_tz_user_id",
                "fieldtype": "Link",
                "options": "User",
                "label": "User ID",
                "insert_after": "hms_tz_submitted_by",
                "read_only": 1,
            },
        ],
        "Radiology Examination": [
            {
                "fieldname": "hms_tz_submit_cb",
                "fieldtype": "Column Break",
                "insert_after": "hms_tz_ref_childname",
            },
            {
                "fieldname": "hms_tz_submitted_by",
                "fieldtype": "Data",
                "label": "Submitted By",
                "insert_after": "hms_tz_submit_cb",
                "read_only": 1,
            },
            {
                "fieldname": "hms_tz_user_id",
                "fieldtype": "Link",
                "options": "User",
                "label": "User ID",
                "insert_after": "hms_tz_submitted_by",
                "read_only": 1,
            },
        ],
        "Clinical Procedure": [
            {
                "fieldname": "hms_tz_submit_cb",
                "fieldtype": "Column Break",
                "insert_after": "hms_tz_ref_childname",
            },
            {
                "fieldname": "hms_tz_submitted_by",
                "fieldtype": "Data",
                "label": "Submitted By",
                "insert_after": "hms_tz_submit_cb",
                "read_only": 1,
            },
            {
                "fieldname": "hms_tz_user_id",
                "fieldtype": "Link",
                "options": "User",
                "label": "User ID",
                "insert_after": "hms_tz_submitted_by",
                "read_only": 1,
            },
        ],
        "Delivery Note": [
            {
                "fieldname": "hms_tz_submitted_by",
                "fieldtype": "Data",
                "label": "Submitted By",
                "insert_after": "column_break_21",
                "read_only": 1,
            },
            {
                "fieldname": "hms_tz_user_id",
                "fieldtype": "Link",
                "options": "User",
                "label": "User ID",
                "insert_after": "hms_tz_submitted_by",
                "read_only": 1,
            },
        ],
    }

    create_custom_fields(fields, update=True)
