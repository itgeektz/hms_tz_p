frappe.ui.form.on('Clinical Procedure', {
    refresh: function(frm) {
        frm.remove_custom_button('Start');
        frm.remove_custom_button('Complete');
    },

    onload: function(frm) {
        frm.remove_custom_button('Start');
        frm.remove_custom_button('Complete');
        if (frm.doc.patient) {
            frm.add_custom_button(__('Patient History'), function () {
                frappe.route_options = { 'patient': frm.doc.patient };
                frappe.set_route('tz-patient-history');
            });
        }
    },
    
    approval_number: (frm) => {
        frm.fields_dict.approval_number.$input.focusout(() => {
            if (frm.doc.approval_number != "" && frm.doc.approval_number != undefined) {
                frappe.dom.freeze(__("Verifying Approval Number..."));
                frappe.call("hms_tz.nhif.api.healthcare_utils.varify_service_approval_number_for_LRPM", {
                    patient: frm.doc.patient,
                    company: frm.doc.company,
                    approval_number: frm.doc.approval_number,
                    template: "Clinical Procedure Template",
                    item: frm.doc.procedure_template,
                }).then(r => {
                    frappe.dom.unfreeze();
                    if (r.message) {
                        frappe.show_alert({
                            message: __("<h4 class='text-center' style='background-color: #D3D3D3; font-weight: bold;'>\
                                Approval Number is Valid</h4>"),
                            indicator: "green"
                        }, 10);
                        let data = r.message;
                        frm.set_value("approval_type", "NHIF");
                        frm.set_value("approval_status", "Verified");
                        frm.set_value("authorized_item_id", data.AuthorizedItemID);
                        frm.set_value("service_authorization_id", data.ServiceAuthorizationID);

                    } else {
                        frm.set_value("approval_number", "");
                        frappe.show_alert({
                            message: __("<h4 class='text-center' style='background-color: #D3D3D3; font-weight: bold;'>\
                                Approval Number is not Valid</h4>"),
                            indicator: "Red"
                        }, 10);
                    }
                });
            }
        });
    }
})