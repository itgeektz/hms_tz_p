import frappe
from frappe.custom.doctype.custom_field.custom_field import create_custom_fields


def create_healthcare_settings_custom_fields():
    custom_fields = {
        "Healthcare Settings": [
            {
                "fieldname": "validate_medical_code_for_cash_patients",
                "label": "Validate Medical Code for Cash Patients",
                "fieldtype": "Check",
                "default": 0,
                "insert_after": "billing_settings_section",
                "description": "Enable medical code validation for cash patients",
            }
        ]
    }

    for doctype, fields in custom_fields.items():
        meta = frappe.get_meta(doctype)
        fields_to_create = []

        for df in fields:
            # ✅ critical: check against meta, not Custom Field table
            if not meta.has_field(df["fieldname"]):
                fields_to_create.append(df)

        if fields_to_create:
            create_custom_fields({doctype: fields_to_create}, update=True)


def execute():
    create_healthcare_settings_custom_fields()
    print("Success")
