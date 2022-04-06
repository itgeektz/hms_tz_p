import frappe

def execute():
    frappe.get_doc({
            'doctype': 'Custom Field',
            'name': 'Patient Encounter-hms_tz_column_break',
            'dt': 'Patient Encounter',
            'fieldname': 'hms_tz_column_break',
            'insert_after': 'get_chronic_diagnosis',
            'fieldtype': 'Column Break'
        }
    ).insert(ignore_permissions=True)

    frappe.get_doc({
            'doctype': 'Custom Field',
            'name': 'Patient Encounter-hms_tz_add_chronic_diagnosis',
            'dt': 'Patient Encounter',
            'label': 'Add Chronic Diagnosis',
            'fieldname': 'hms_tz_add_chronic_diagnosis',
            'insert_after': 'hms_tz_column_break',
            'fieldtype': 'Button',
            "depends_on": "eval: doc.docstatus == 0",
        }
    ).insert(ignore_permissions=True)

    section_break_64 = frappe.get_doc('Custom Field', 'Patient Encounter-section_break_64')
    section_break_64.insert_after = 'hms_tz_add_chronic_diagnosis'
    section_break_64.save(ignore_permissions=True)

    patient_encounter_preliminary_diagnosis = frappe.get_doc('Custom Field', 
        'Patient Encounter-patient_encounter_preliminary_diagnosis'
    )
    patient_encounter_preliminary_diagnosis.insert_after = 'section_break_64'
    patient_encounter_preliminary_diagnosis.save(ignore_permissions=True)

    frappe.get_doc({
            'doctype': 'Custom Field',
            'name': 'Inpatient Consultancy-hms_tz_invoiced',
            'dt': 'Inpatient Consultancy',
            'label': 'Invoiced',
            'fieldname': 'hms_tz_invoiced',
            'insert_after': 'encounter',
            'fieldtype': 'Check'
        }
    ).insert(ignore_permissions=True)

    is_confirmed = frappe.get_doc('Custom Field', 'Inpatient Consultancy-is_confirmed')
    is_confirmed.insert_after = 'hms_tz_invoiced'
    is_confirmed.save(ignore_permissions=True)

    frappe.db.commit()
    