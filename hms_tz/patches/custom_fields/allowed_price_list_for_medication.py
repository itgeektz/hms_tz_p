from frappe.custom.doctype.custom_field.custom_field import create_custom_fields


def execute():
    fields = {
        "Company": [
            {
                "fieldname": "allow_filtered_medication_on_patient_encounter",
                "fieldtype": "Check",
                "label": "Allow Filtered Medication on Patient Encounter",
                "insert_after": "hms_tz_settings_sb",
                "description": "Allow to filter medication on Patient Encounter based on allowed price list settled on each medication record",
            }
        ],
        "Medication": [
            {
                "fieldname": "allowed_price_lists",
                "fieldtype": "Table",
                "options": "Allowed Price List",
                "label": "Allowed Price Lists",
                "insert_after": "staff_role",
                "read_only": 0,
                "allow_on_submit": 0,
            }
        ],
    }

    create_custom_fields(fields, update=True)
