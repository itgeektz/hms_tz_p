import frappe
from frappe.custom.doctype.custom_field.custom_field import create_custom_fields

def execute():
    fields = {
        "Patient Encounter": [
            dict(
                fieldname="hms_tz_column_break",
                fieldtype="Column Break",
                label="",
                insert_after="get_chronic_diagnosis",
            ),
            dict(
                fieldname="hms_tz_add_chronic_diagnosis",
                fieldtype="Button",
                label="Add Chronic Diagnosis",
                insert_after="hms_tz_column_break",
                depends_on="eval: doc.docstatus == 0"
            ),
            dict(
                fieldname="hms_tz_section_break",
                fieldtype="Section Break",
                label="",
                insert_after="hms_tz_add_chronic_diagnosis",
            )
        ],
        "Inpatient Consultancy": [
            dict(
                fieldname="hms_tz_invoiced",
                fieldtype="Check",
                label="Invoiced",
                insert_after="encounter",
            )
        ]
    }
    create_custom_fields(fields, update=True)

    patient_encounter_preliminary_diagnosis = frappe.get_doc('Custom Field', 
        'Patient Encounter-patient_encounter_preliminary_diagnosis'
    )
    patient_encounter_preliminary_diagnosis.insert_after = 'hms_tz_section_break'
    patient_encounter_preliminary_diagnosis.save(ignore_permissions=True)

    is_confirmed = frappe.get_doc('Custom Field', 'Inpatient Consultancy-is_confirmed')
    is_confirmed.insert_after = 'hms_tz_invoiced'
    is_confirmed.save(ignore_permissions=True)

    frappe.db.commit()
    