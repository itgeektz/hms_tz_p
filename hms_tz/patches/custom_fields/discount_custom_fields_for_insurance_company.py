import frappe
from frappe.custom.doctype.custom_field.custom_field import create_custom_fields

def execute():
    fields = {
        "Healthcare Insurance Company": [
            dict(
                fieldname="hms_tz_has_price_discount",
                fieldtype="Check",
                label="Has Price Discount",
                insert_after="disabled"
            ),
            dict(
                fieldname="hms_tz_price_discount",
                fieldtype="Percent",
                label="Price Discount(%)",
                insert_after="hms_tz_has_price_discount",
                depends_on="eval: doc.hms_tz_has_price_discount == 1",
                mandatory_depends_on="eval: doc.hms_tz_has_price_discount == 1",
                bold=1
            )
        ],
        "Patient Appointment": [
            dict(
                fieldname="hms_tz_is_discount_applied",
                fieldtype="Check",
                label="Is Discount Applied",
                insert_after="paid_amount",
                description="Discount is applied only if the discount percent is defined on Healthcare Insurance Company",
                read_only=1
            )
        ],
        "Lab Prescription": [
            dict(
                fieldname="hms_tz_is_discount_applied",
                fieldtype="Check",
                label="Is Discount Applied",
                insert_after="amount",
                description="Discount is applied only if the discount percent is defined on Healthcare Insurance Company",
                read_only=1
            )
        ],
        "Radiology Procedure Prescription": [
            dict(
                fieldname="hms_tz_is_discount_applied",
                fieldtype="Check",
                label="Is Discount Applied",
                insert_after="amount",
                description="Discount is applied only if the discount percent is defined on Healthcare Insurance Company",
                read_only=1
            )
        ],
        "Procedure Prescription": [
            dict(
                fieldname="hms_tz_is_discount_applied",
                fieldtype="Check",
                label="Is Discount Applied",
                insert_after="amount",
                description="Discount is applied only if the discount percent is defined on Healthcare Insurance Company",
                read_only=1
            )
        ],
        "Drug Prescription": [
            dict(
                fieldname="hms_tz_is_discount_percent",
                fieldtype="Percent",
                label="Discount (%) on Price",
                insert_after="update_schedule",
                read_only=1
            ),
            dict(
                fieldname="hms_tz_is_discount_applied",
                fieldtype="Check",
                label="Is Discount Applied",
                insert_after="hms_tz_is_discount_percent",
                description="Discount is applied only if the discount percent is defined on Healthcare Insurance Company",
                read_only=1
            ),
        ],
        "Therapy Plan Detail": [
            dict(
                fieldname="hms_tz_is_discount_applied",
                fieldtype="Check",
                label="Is Discount Applied",
                insert_after="amount",
                description="Discount is applied only if the discount percent is defined on Healthcare Insurance Company",
                read_only=1
            )
        ],
        "Inpatient Occupancy": [
            dict(
                fieldname="hms_tz_is_discount_applied",
                fieldtype="Check",
                label="Is Discount Applied",
                insert_after="amount",
                description="Discount is applied only if the discount percent is defined on Healthcare Insurance Company",
                read_only=1
            )
        ],
        "Inpatient Consultancy": [
            dict(
                fieldname="hms_tz_is_discount_applied",
                fieldtype="Check",
                label="Is Discount Applied",
                insert_after="rate",
                description="Discount is applied only if the discount percent is defined on Healthcare Insurance Company",
                read_only=1
            )
        ],
        "Delivery Note Item": [
            dict(
                fieldname="hms_tz_is_discount_applied",
                fieldtype="Check",
                label="Is Discount Applied",
                insert_after="amount",
                description="Discount is applied only if the discount percent is defined on Healthcare Insurance Company",
                read_only=1
            )
        ],
        "Original Delivery Note Item": [
            dict(
                fieldname="hms_tz_is_discount_applied",
                fieldtype="Check",
                label="Is Discount Applied",
                insert_after="amount",
                description="Discount is applied only if the discount percent is defined on Healthcare Insurance Company",
                read_only=1
            )
        ]
    }

    create_custom_fields(fields, update=True)