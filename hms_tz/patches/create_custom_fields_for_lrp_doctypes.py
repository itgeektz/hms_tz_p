import frappe
from frappe.custom.doctype.custom_field.custom_field import create_custom_fields

def execute():
    fields = {
        "Lab Test": [
            dict(
                fieldname="hms_tz_ref_childname",
                fieldtype="Data",
                label="Ref Childname",
                insert_after="ref_docname",
                read_only=1
            )
        ],
        "Radiology Examination": [
            dict(
                fieldname="hms_tz_ref_childname",
                fieldtype="Data",
                label="Ref Childname",
                insert_after="ref_docname",
                read_only=1
            )
        ],
        "Clinical Procedure": [
            dict(
                fieldname="hms_tz_ref_childname",
                fieldtype="Data",
                label="Ref Childname",
                insert_after="ref_docname",
                read_only=1
            )
        ]}

    create_custom_fields(fields, update=True)