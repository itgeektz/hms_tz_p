// Copyright (c) 2023, Aakvatech and contributors
// For license information, please see license.txt

frappe.ui.form.on('NHIF Tracking Claim Change', {
	refresh: function(frm) {
		frm.add_custom_button(__("View Report"), function () {
			frappe.route_options = {"company": frm.doc.company, "claim_month": frm.doc.claim_month, "claim_year": frm.doc.claim_year};
			frappe.set_route("query-report", "NHIF Tracking Claim Change Report");
		});
	}
});
