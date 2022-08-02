import frappe
from frappe.custom.doctype.custom_field.custom_field import create_custom_fields

def execute():
    field = {
        "Clinical Procedure Template": [
            dict(
                fieldname="is_inpatient",
                fieldtype="Check",
                label="Is Inpatient",
                insert_after="is_not_completed",
                description="If ticked, this procedure will be provided to admitted patient only"
            )
        ]
    }
    create_custom_fields(field, update=True)