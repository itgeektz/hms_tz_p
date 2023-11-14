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
                if (!frm.doc.insurance_company.includes("NHIF")) {
                    return;
                }

                frappe.call({
                    method: "hms_tz.nhif.api.healthcare_utils.varify_service_approval_number_for_LRPM", 
                    args: {
                        company: frm.doc.company,
                        approval_number: frm.doc.approval_number,
                        template_doctype: "Clinical Procedure Template",
                        template_name: frm.doc.procedure_template,
                        encounter: frm.doc.ref_docname
                    },
                    freeze: true,
                    freeze_message: __('<i class="fa fa-spinner fa-spin fa-4x"></i>'),
                }).then(r => {
                    if (r.message && r.message == "approval number validation is disabled") {
                        return
                    }
                    else if (r.message) {
                        frappe.show_alert({
                            message: __("<h4 class='text-center' style='background-color: #D3D3D3; font-weight: bold;'>\
                                Approval Number is Valid</h4>"),
                            indicator: "green"
                        }, 20);

                    } else {
                        frm.set_value("approval_number", "");
                        frappe.show_alert({
                            message: __("<h4 class='text-center' style='background-color: #D3D3D3; font-weight: bold;'>\
                                Approval Number is not Valid</h4>"),
                            indicator: "Red"
                        }, 20);
                    }
                });
            }
        });
    }
})