// Copyright (c) 2020, Aakvatech and contributors
// For license information, please see license.txt

frappe.ui.form.on('NHIF Patient Claim', {
	setup: function(frm) {
		frm.set_query("patient_appointment", function() {
			return {
				"filters": {
                    "nhif_patient_claim": ["in", ["", "None"]],
					"insurance_company": "NHIF",
					"insurance_subscription": ["not in",["", "None"]]
				}
			};
		});
	}
});
