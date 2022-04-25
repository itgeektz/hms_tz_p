import frappe
from frappe.custom.doctype.custom_field.custom_field import create_custom_fields

def execute():
    custom_field = {'Sales Invoice Item': [dict(fieldname='hms_tz_is_lrp_item_created',
            label='Is LRP Item Created', fieldtype='Check', insert_after='reference_dn',
            depends_on='eval: doc.reference_dt=="Lab Prescription" || doc.reference_dt==Radiology Procedure Prescription ||\
                doc.reference_dt=="Procedure Prescription" ',
            allow_on_submit=1, read_only=1, bold=1,)]
        }
    create_custom_fields(custom_field, update=True)

    # Update/tick a check box for a new custom field 'hms_tz_is_lrpt_item_created' to all previous transactions
    today_date = frappe.utils.nowdate()
    frappe.db.sql("""
        UPDATE `tabSales Invoice Item` sii
        INNER JOIN `tabSales Invoice` si ON sii.parent = si.name
        SET sii.hms_tz_is_lrp_item_created = 1
        WHERE si.patient is not null
        AND si.docstatus = 1
        AND si.posting_date <= %s
        AND sii.reference_dt IN ("Lab Prescription", "Radiology Procedure Prescription", "Procedure Prescription")
    """, today_date)
