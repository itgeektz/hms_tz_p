import frappe
from frappe.custom.doctype.custom_field.custom_field import create_custom_fields

def execute():
    fields = {
        "Company": [
            {
                "fieldname": "hms_tz_settings_sb",
                "label": "HMS TZ Settings",
                "fieldtype": "Section Break",
                "insert_after": "date_of_establishment",
                "collapsible": 1,
            },
            {
                "fieldname": "hms_tz_has_cash_limit_alert",
                "label": "Has Cash Limit Alert",
                "fieldtype": "Check",
                "insert_after": "hms_tz_settings_sb",
                "default": 1,
            },
            {
                "fieldname": "hms_tz_minimum_cash_limit_percent",
                "label": "Minimum Cash Limit Percent",
                "fieldtype": "Int",
                "insert_after": "hms_tz_has_cash_limit_alert",
                "default": 10,
                "mandatory_depends_on": "eval:doc.hms_tz_has_cash_limit_alert == 1",
                "description": "Minimum cash limit percent to warn/stop doctor.",
            },
            {
                "fieldname": "cash_limit_cb",
                "fieldtype": "Column Break",
                "insert_after": "hms_tz_minimum_cash_limit_percent",
            },
            {
                "fieldname": "hms_tz_limit_under_minimum_percent_action",
                "label": "Limit Under Minimum Percent Action",
                "fieldtype": "Select",
                "insert_after": "cash_limit_cb",
                "options": "\nWarn\nStop\nIgnore",
                "default": "Warn",
                "mandatory_depends_on": "eval:doc.hms_tz_has_cash_limit_alert == 1",
                "description": "Action to take on doctor level when cash limit is under minimum percent.",
            },
            {
                "fieldname": "hms_tz_limit_exceed_action",
                "label": "Limit Exceed Action",
                "fieldtype": "Select",
                "insert_after": "hms_tz_limit_under_minimum_percent_action",
                "options": "\nWarn\nStop\nIgnore",
                "default": "Stop",
                "mandatory_depends_on": "eval:doc.hms_tz_has_cash_limit_alert == 1",
                "description": "Action to take on doctor level when cash limit is exceeded.",
            },
        ]
    }

    create_custom_fields(fields, update=True)