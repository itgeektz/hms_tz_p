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
        ],
        "Healthcare Insurance Subscription": [
            dict(
                fieldname="hms_tz_scheme_section_break",
                label="Product and Scheme Details",
                fieldtype="Section Break",
                insert_after="coverage_plan_card_number",
            ),
            dict(
                fieldname="hms_tz_product_code",
                label="Product Code",
                fieldtype="Data",
                insert_after="hms_tz_scheme_section_break",
            ),
            dict(
                fieldname="hms_tz_product_name",
                label="Product Name",
                fieldtype="Data",
                insert_after="hms_tz_product_code",
            ),
            dict(
                fieldname="hms_tz_scheme_column_break",
                label="",
                fieldtype="Column Break",
                insert_after="hms_tz_product_name",
            ),
             dict(
                fieldname="hms_tz_scheme_id",
                label="SchemeId",
                fieldtype="Data",
                insert_after="hms_tz_scheme_column_break",
            ),
             dict(
                fieldname="hms_tz_scheme_name",
                label="Scheme Name",
                fieldtype="Data",
                insert_after="hms_tz_scheme_id",
            ),
        ]
    }
    create_custom_fields(fields)