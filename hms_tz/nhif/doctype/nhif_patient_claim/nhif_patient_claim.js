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
		if (frm.doc.patient && frm.doc.patient_appointment) {
			frappe.db.get_list('LRPMT Returns', {
				fields:['name'],
				filters:{
					'patient': frm.doc.patient, 
					'appointment_no': frm.doc.patient_appointment,
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
							<p class='text-left'>This Patient: <b>${__(frm.doc.patient)}</b> of appointmentNo: <b>${__(frm.doc.patient_appointment)}</b>
							having some item(s) cancelled or some quantity of item(s) returned to stock, by <b>${__(msg_lrpmt)}</b>,
							inorder for items and their quantities to be reflected on this claim</p>
							<p class='text-center' style='background-color: #FFA500; font-size: 14px;'>
							<strong><em><i>Tick allow changes then, Save this claim then, Untick allow changes and Save again</i></em></strong></p>
							`
						)
					});
				}
			});
		};

		if (frm.doc.authorization_no) {
			frm.add_custom_button(__("Merge Claims"), function () {
				frappe.call({
					method: "hms_tz.nhif.doctype.nhif_patient_claim.nhif_patient_claim.merge_nhif_claims",
					args: { "authorization_no": frm.doc.authorization_no },
					callback: function (data) {
						frm.reload_doc()
					}
				})
			})
		}
	}
});