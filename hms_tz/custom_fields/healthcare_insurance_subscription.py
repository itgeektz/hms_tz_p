import frappe
from frappe.custom.doctype.custom_field.custom_field import create_custom_fields

def create_patient_encounter_custom_fields():

    from frappe.custom.doctype.custom_field.custom_field import create_custom_fields
    """
    Custom fields for Patient Encounter
    - Insurance and payment related fields required by hms_tz customizations
    """
    
    custom_fields = {
        "Patient Encounter": [
            {
                "fieldname": "insurance_subscription",
                "label": "Insurance Subscription",
                "fieldtype": "Link",
                "options": "Healthcare Insurance Subscription",
                "insert_after": "insurance_company",
                "depends_on": "eval:doc.insurance_company",
                "fetch_from": "",
                "read_only": 0,
                "in_list_view": 0,
                "in_standard_filter": 1,
                "description": "Patient's insurance subscription for this encounter"
            },
            {
                "fieldname": "insurance_company",
                "label": "Insurance Company",
                "fieldtype": "Link",
                "options": "Healthcare Insurance Company",
                "insert_after": "company",
                "read_only": 0,
                "in_list_view": 0,
                "in_standard_filter": 1,
                "description": "Healthcare insurance company for this encounter"
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
                "in_list_view": 0,
                "description": "Coverage plan from the insurance subscription (auto-fetched)"
            },
            {
                "fieldname": "mode_of_payment",
                "label": "Mode of Payment",
                "fieldtype": "Link",
                "options": "Mode of Payment",
                "insert_after": "company",
                "read_only": 0,
                "in_list_view": 0,
                "in_standard_filter": 1,
                "description": "Payment mode for cash patients"
            },
            {
                "fieldname": "price_list",
                "label": "Price List",
                "fieldtype": "Link",
                "options": "Price List",
                "insert_after": "mode_of_payment",
                "read_only": 1,
                "in_list_view": 0,
                "description": "Price list for this encounter (auto-set from insurance or mode of payment)"
            }
        ]
    }
    
    create_custom_fields(custom_fields, update=True)
    print("✓ Custom fields created successfully for Patient Encounter")
    print("  - insurance_subscription")
    print("  - insurance_company")
    print("  - insurance_coverage_plan")
    print("  - mode_of_payment")
    print("  - price_list")

def execute():
    """Execute function for bench migrate"""
    create_patient_encounter_custom_fields()