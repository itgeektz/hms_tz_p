// Copyright (c) 2020, Aakvatech and contributors
// For license information, please see license.txt

frappe.ui.form.on('NHIF Patient Claim', {
	setup: function (frm) {
		frm.set_query("patient_appointment", function () {
			return {
				"filters": {
					"nhif_patient_claim": ["in", ["", "None"]],
					"insurance_company": ["like", "NHIF%"],
					"insurance_subscription": ["not in", ["", "None"]]
				}
			};
		});
	},

	refresh(frm) {
		if (frm.doc.docstatus === 0 && frm.doc.authorization_no) {
			frm.add_custom_button(__("Merge Claims"), function () {
				frm.dirty()
				frm.call('get_appointments', {self: frm.doc})
				.then(r => {
					frm.save()
					frm.refresh()
				});
			});
		}
	},

	onload: function(frm) {
		if (frm.doc.patient && frm.doc.patient_appointment) {
			frappe.db.get_list('LRPMT Returns', {
				fields:['name'],
				filters:{
					'patient': frm.doc.patient, 
					'appointment': frm.doc.patient_appointment,
					'docstatus': 1
				}
			}).then(data => {
				if (data.length > 0) {
					let msg_lrpmt = ``
					data.forEach(element => {
						msg_lrpmt += `${__(element.name)} ,`
					});

					frappe.msgprint({
						title: __('Notification'),
						indicator: 'orange',
						message: __(`
							<p class='text-left'>This Patient: <b>${__(frm.doc.patient)}</b> of appointment No: <b>${__(frm.doc.patient_appointment)}</b>
							having some item(s) cancelled or some quantity of item(s) returned to stock, by <b>${__(msg_lrpmt)}</b>,
							inorder for items and their quantities to be reflected on this claim</p>
							<p class='text-center' style='background-color: #FFA500; font-size: 14px;'>
							<strong><em><i>Tick allow changes, then Untick allow changes and Save again</i></em></strong></p>
							`
						)
					});
				}
			});
		};
	},

	is_ready_for_auto_submission: (frm) => {
		if (frm.doc.is_ready_for_auto_submission == 1) {
			frm.set_value("reviewed_by", frappe.user.full_name());
		} else {
			frm.set_value("reviewed_by", "");
		}
	}
});