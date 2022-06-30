// Copyright (c) 2022, Aakvatech and contributors
// For license information, please see license.txt

frappe.ui.form.on('Healthcare Referral', {
	refresh: function(frm) {
		if (!frm.doc.referral_no || frm.doc.referral_status != "Success") {
			frm.add_custom_button(__("Get Referral No"), () => {
				frappe.call({
					method: "hms_tz.nhif.doctype.healthcare_referral.healthcare_referral.get_referral_no",
					args: {name: frm.doc.name },
					freeze: true
				}).then(r => {
					if (r.message.referralno) {
						frm.refresh();
						frappe.msgprint(__("<b>Referral No:</b> {0}", [r.message.referralno]));
					}
				})
			}).addClass("btn-primary");
		}

	}
});
