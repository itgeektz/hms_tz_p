import frappe
from frappe.custom.doctype.custom_field.custom_field import create_custom_fields

def execute():
    fields = {
        "Delivery Note": [
            dict(
                fieldname='hms_tz_phone_no',
                fieldtype='Data',
                label='Phone Number',
                insert_after='patient_name',
                read_only=1
            ),
            dict(
                fieldname="hms_tz_appointment_no",
                fieldtype="Data",
                label="Appointment Number",
                insert_after="coverage_plan_name",
                fetch_from="reference_name.appointment",
                fetch_if_empty=1,
                read_only=1
            )
        ]
    }
    create_custom_fields(fields, update=True)

    practitioner = frappe.get_doc('Custom Field', 'Delivery Note-healthcare_practitioner')
    practitioner.insert_after = 'healthcare_service_unit'
    practitioner.read_only = 1
    practitioner.save(ignore_permissions=True)

    frappe.db.commit()