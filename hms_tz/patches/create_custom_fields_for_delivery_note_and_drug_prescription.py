import frappe
from frappe.custom.doctype.custom_field.custom_field import create_custom_fields


def execute():
    frappe.reload_doc('nhif', 'doctype', 'original_delivery_note_item', force=True)
    frappe.db.commit()

    fields = {
        "Delivery Note": [
            dict(
                fieldname="hms_tz_all_items_out_of_stock",
                label="All Items Out of Stock",
                fieldtype="Check",
                insert_after="authorization_number",
                hidden=1,
                read_only=1,
            ),
            dict(
                fieldname="original_prescription",
                label="Original Prescription",
                fieldtype="Section Break",
                insert_after="items",
            ),
            dict(
                fieldname="hms_tz_original_items",
                label="Original Items",
                fieldtype="Table",
                insert_after="original_prescription",
                options="Original Delivery Note Item",
                read_only=1,
            ),
        ],
        "Delivery Note Item": [
            dict(
                fieldname="hms_tz_is_out_of_stock",
                label="Is Out of Stock",
                fieldtype="Check",
                insert_after="customer_item_code",
                bold=1,
            )
        ],
        "Drug Prescription": [
            dict(
                fieldname="is_not_available_inhouse",
                label="Is Not Available Inhouse",
                fieldtype="Check",
                insert_after="prescribe",
                allow_on_submit=1,
                read_only=1,
                bold=1,
            ),
            dict(
                fieldname="hms_tz_is_out_of_stock",
                label="Is Out of Stock",
                fieldtype="Check",
                insert_after="is_not_available_inhouse",
                allow_on_submit=1,
                read_only=1,
                bold=1,
            ),
        ],
    }

    create_custom_fields(fields, update=True)
