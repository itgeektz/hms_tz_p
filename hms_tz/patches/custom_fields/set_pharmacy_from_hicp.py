import frappe
from frappe.custom.doctype.custom_field.custom_field import create_custom_fields


def execute():
    fields = {
        "Healthcare Insurance Coverage Plan": [
            {
                "fieldname": "opd_insurance_pharmacy",
                "fieldtype": "Link",
                "label": "OPD Insurance Pharmacy",
                "options": "Healthcare Service Unit",
                "insert_after": "hms_tz_submit_encounter_on_limit_exceed",
                "reqd": 1,
                "description": "This pharmacy will be auto set on patient encounter, for OPD patients of this coverage plan",
            },
            {
                "fieldname": "ipd_insurance_pharmacy",
                "fieldtype": "Link",
                "label": "IPD Insurance Pharmacy",
                "options": "Healthcare Service Unit",
                "insert_after": "opd_insurance_pharmacy",
                "reqd": 1,
                "description": "This pharmacy will be auto set on patient encounter, for IPD patients of this coverage plan",
            },
        ]
    }

    create_custom_fields(fields, update=True)
