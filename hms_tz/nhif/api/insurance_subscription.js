frappe.ui.form.on('Healthcare Insurance Subscription', {
    setup: function (frm) {
        frm.set_query('healthcare_insurance_coverage_plan', function () {
			return {
				filters: { 'insurance_company': frm.doc.insurance_company }
			};
		});
    },
});