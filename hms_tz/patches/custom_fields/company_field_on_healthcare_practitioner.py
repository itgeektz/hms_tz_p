import frappe
from frappe.custom.doctype.custom_field.custom_field import create_custom_fields

def execute():
    fields = {
        "healthcare Practitioner": [
            dict(
                fieldname="hms_tz_company",
                fieldtype="Link",
                label="Company",
                insert_after="status",
                options="Company",
                reqd=1
            )
        ]
    }
    
    create_custom_fields(fields, update=True)