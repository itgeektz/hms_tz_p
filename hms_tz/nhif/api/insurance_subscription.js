frappe.ui.form.on('Healthcare Insurance Subscription', {
    setup: function (frm) {
        frm.set_query('healthcare_insurance_coverage_plan', function () {
			return {
				filters: { 'insurance_company': frm.doc.insurance_company }
			};
		});
    },
    coverage_plan_card_number: function(frm){
        if (!frm.doc.coverage_plan_card_number) return
        frappe.call({
            method: 'hms_tz.nhif.api.insurance_subscription.check_patient_info',
            args: {
                'card_no': frm.doc.coverage_plan_card_number,
                'patient': frm.doc.patient,
                'patient_name': frm.doc.patient_name
            },
            callback: function (data) {
                if (data.message && data.message != frm.doc.patient_name) {
                    frm.set_value("patient_name", data.message);
                }
            }
        });
    },
});