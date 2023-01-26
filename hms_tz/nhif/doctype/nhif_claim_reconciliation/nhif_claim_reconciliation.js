// Copyright (c) 2022, Aakvatech and contributors
// For license information, please see license.txt

frappe.ui.form.on('NHIF Claim Reconciliation', {
	refresh: function(frm) {
		
	},

	get_detail: (frm) => {
		if (frm.doc.status == "Pending") {
			frappe.call({
				method: "hms_tz.nhif.doctype.nhif_claim_reconciliation.nhif_claim_reconciliation.get_submitted_claims",
				args: {
					self: frm.doc
				},
				freeze: true,
				callback: function(r) {
					if (r.message) {
						frm.refresh();
					}
				}
			});
		}
	}
});
