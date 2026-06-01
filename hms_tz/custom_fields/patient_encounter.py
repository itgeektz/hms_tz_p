import frappe
from frappe.custom.doctype.custom_field.custom_field import create_custom_fields


def create_patient_encounter_custom_fields():
    custom_fields = {
        "Patient Encounter": [
            {
                "fieldname": "mode_of_payment",
                "label": "Mode of Payment",
                "fieldtype": "Link",
                "options": "Mode of Payment",
                "insert_after": "company",
                "in_standard_filter": 1,
            },
            {
                "fieldname": "price_list",
                "label": "Price List",
                "fieldtype": "Link",
                "options": "Price List",
                "insert_after": "mode_of_payment",
                "read_only": 1,
            },
            {
                "fieldname": "insurance_company",
                "label": "Insurance Company",
                "fieldtype": "Link",
                "options": "Healthcare Insurance Company",
                "insert_after": "price_list",
                "in_standard_filter": 1,
            },
            {
                "fieldname": "insurance_subscription",
                "label": "Insurance Subscription",
                "fieldtype": "Link",
                "options": "Healthcare Insurance Subscription",
                "insert_after": "insurance_company",
                "depends_on": "eval:doc.insurance_company",
                "in_standard_filter": 1,
            },
            {
                "fieldname": "insurance_coverage_plan",
                "label": "Insurance Coverage Plan",
                "fieldtype": "Link",
                "options": "Healthcare Insurance Coverage Plan",
                "insert_after": "insurance_subscription",
                "depends_on": "eval:doc.insurance_subscription",
                "fetch_from": "insurance_subscription.healthcare_insurance_coverage_plan",
                "read_only": 1,
            },
        ]
    }

    for doctype, fields in custom_fields.items():
        meta = frappe.get_meta(doctype)
        fields_to_create = []

        for df in fields:
            # ✅ THIS is the critical fix
            if not meta.has_field(df["fieldname"]):
                fields_to_create.append(df)

        if fields_to_create:
            create_custom_fields({doctype: fields_to_create}, update=True)


def execute():
    create_patient_encounter_custom_fields()
