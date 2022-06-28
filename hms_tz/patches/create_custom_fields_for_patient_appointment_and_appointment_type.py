import frappe
from frappe.custom.doctype.custom_field.custom_field import create_custom_fields

def execute():
    fields={
        "Patient Appointment": [
            dict(
                fieldname="remarks",
                label="Remarks",
                fieldtype="Small Text",
                insert_after="referral_no",
                translatable=1,
            ),
        ],
        "Appointment Type": [
            dict(
                fieldname="source",
                label="Source",
                fieldtype="Data",
                insert_after="visit_type_id",
                reqd=1,
                translatable=1,
            )
        ]
    }
    create_custom_fields(fields)