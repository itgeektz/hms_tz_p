frappe.ui.form.on('Healthcare Service Order', {
    clear_insurance_details: function(frm) {
        if (!frm.doc.insurance_claim) {return}
        frappe.call({
            method: 'hms_tz.nhif.api.service_order.clear_insurance_details',
            args: {
                'service_order': frm.doc.name
            },
            callback: function (data) {
                if (!data.exc) {
                    frm.reload_doc()
                }
            }
        });
    }
});