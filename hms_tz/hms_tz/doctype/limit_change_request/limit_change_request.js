// Copyright (c) 2021, Aakvatech and contributors
// For license information, please see license.txt

frappe.ui.form.on('Limit Change Request', {
	refresh: function (frm) {
		frm.set_query("appointment_no", () => {
			return {
				filters: {
					"patient": frm.doc.patient,
					"status": "Closed"
				}
			};
		})
	}
});

