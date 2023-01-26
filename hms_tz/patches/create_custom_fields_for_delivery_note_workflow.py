import frappe
from frappe.custom.doctype.custom_field.custom_field import create_custom_fields


def execute():
    fields = {
        "Delivery Note": [
            dict(
                fieldname="hms_tz_comment",
                fieldtype="Small Text",
                label="Comment",
                insert_after="set_target_warehouse",
                depends_on="eval: doc.docstatus == 0 && doc.is_return == 0 && doc.workflow_state != 'Not Serviced'",
                description="comment to indicate an item that required to be changed in case you want to create medication change request",
            ),
            dict(
                fieldname="hms_tz_lrpmt_returns",
                fieldtype="Button",
                label="LRPMT Returns",
                insert_after="hms_tz_comment",
                allow_on_submit=1,
                depends_on = "eval: doc.is_return == 0 && doc.workflow_state != 'Not Serviced' "
            ),
            dict(
                fieldname="hms_tz_medicatiion_change_request",
                fieldtype="Button",
                label="Medicatiion Change Request",
                insert_after="hms_tz_lrpmt_returns",
                depends_on="eval: doc.docstatus == 0 && doc.is_return == 0 && doc.workflow_state != 'Not Serviced'"
            ),
        ],
        "Medication Change Request": [
            dict(
                fieldname="hms_tz_comment",
                fieldtype="Small Text",
                label="Comment",
                insert_after="appointment",
                description="comment indicates an item that required to be changed",
                read_only=1,
            )
        ],
        "LRPMT Returns": [
            dict(
                fieldname="hms_tz_help_msg_section_break",
                fieldtype="Section Break",
                label="",
                insert_after="",
                idx=1
            ),
            dict(
                fieldname="hms_tz_lrpmt_returns_help_msg",
                fieldtype="HTML",
                label="",
                insert_after="hms_tz_help_msg_section_break",
                options="<div class='alert alert-warning'>\
				    LRPMT Returns can be used to:<br>\
                        1. Cancel draft and submitted lab test, radiology examination and clinical procedure<br>\
                        2. Cancel non-created lab test, radiology examination and clinical procedure to remove them from itemized bill<br>\
                        3. Cancel non-created drug items to remove them from itemized bill<br>\
                        4. Cancel whole draft delivery note, even if one item of draft delivery note is selected<br>\
                        5. Return quantities of submitted delivery note\
			    </div>"
            ),
            dict(
                fieldname="hms_tz_patient_info",
                fieldtype="Section Break",
                label="",
                insert_after="hms_tz_lrpmt_returns_help_msg",
            )
        ]
    }

    create_custom_fields(fields, update=True)


