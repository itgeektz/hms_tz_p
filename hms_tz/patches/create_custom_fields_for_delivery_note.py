import frappe

def execute():
    frappe.get_doc({
        'doctype': 'Custom Field',
        'name': 'Delivery Note-hms_tz_phone_no',
        'dt': 'Delivery Note',
        'label': 'Phone Number',
        'fieldname': 'hms_tz_phone_no',
        'insert_after': 'patient_name',
        'fieldtype': 'Data',
        'read_only': 0
    }).insert(ignore_permissions=True)

    frappe.get_doc({
        'doctype': 'Custom Field',
        'name': 'Delivery Note-hms_tz_appointment_no',
        'dt': 'Delivery Note',
        'label': 'Appointment Number',
        'fieldname': 'hms_tz_appointment_no',
        'insert_after': 'coverage_plan_name',
        'fieldtype': 'Data',
        'fetch_from': 'reference_name.appointment',
        'fetch_if_empty': 1,
        'read_only': 1
    }).insert(ignore_permissions=True)

    frappe.get_doc({
        'doctype': 'Custom Field',
        'name': 'Delivery Note-hms_tz_practitioner',
        'dt': 'Delivery Note',
        'label': 'Practitioner',
        'fieldname': 'hms_tz_practitioner',
        'insert_after': 'hms_tz_appointment_no',
        'fieldtype': 'Data',
        'fetch_from': 'reference_name.practitioner',
        'fetch_if_empty': 1,
        'read_only': 1
    }).insert(ignore_permissions=True)

    frappe.db.commit()