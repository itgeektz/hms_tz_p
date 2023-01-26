import frappe
from frappe.custom.doctype.property_setter.property_setter import make_property_setter

def execute():
    properties = [
        {
            "doctype": "Lab Test",
            "fieldname": "insurance_section",
            "property": "hidden",
            "value": 0,
            "property_type": "Check"
        },
        {
            "doctype": "Lab Test",
            "fieldname": "insurance_subscription",
            "property": "read_only",
            "value": 1,
            "property_type": "Check"
        },
        {
            "doctype": "Radiology Examination", 
            "fieldname": "insurance_section",
            "property": "hidden",
            "value": 0,
            "property_type": "Check"
        },
        {
            "doctype": "Radiology Examination", 
            "fieldname": "insurance_subscription",
            "property": "read_only",
            "value": 1,
            "property_type": "Check"
        },
        {
            "doctype": "Clinical Procedure", 
            "fieldname": "insurance_section",
            "property": "hidden",
            "value": 0,
            "property_type": "Check"
        },
        {
            "doctype": "Therapy Session", 
            "fieldname": "appointment",
            "property": "fetch_from",
            "value": "therapy_plan.hms_tz_appointment",
            "property_type": "Small Text"
        },
        {
            "doctype": "Therapy Session",
            "fieldname": "appointment",
            "property": "fetch_if_empty",
            "value": 1,
            "property_type": "Check"
        },
    ]

    for property in properties:
        make_property_setter(
            property.get("doctype"),
            property.get("fieldname"),
            property.get("property"),
            property.get("value"),
            property.get("property_type"),
            for_doctype=False,
            validate_fields_for_doctype=False
        )
    
    frappe.db.commit()