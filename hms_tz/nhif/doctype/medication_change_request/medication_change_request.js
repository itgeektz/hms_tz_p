// Copyright (c) 2021, Aakvatech and contributors
// For license information, please see license.txt

frappe.ui.form.on('Medication Change Request', {
	setup: (frm) => {
		frm.set_query('appointment', function () {
			return {
				filters: { 'patient': frm.doc.patient }
			};
		});
		frm.set_query('patient_encounter', function () {
			return {
				filters: {
					'patient': frm.doc.patient,
				}
			};
		});
		frm.set_query('delivery_note', function () {
			return {
				filters: {
					'patient': frm.doc.patient,
					'reference_name': frm.doc.patient_encounter
				}
			};
		});
	},

	patient_encounter: (frm) => {
		set_delivery_note(frm);
		update_childs_tables(frm);
	},

	delivery_note: (frm) => {
		set_patient_encounter(frm);
	},
	patient: (frm) => {
		frm.set_value("patient_encounter", '');
		frm.set_value("delivery_note", '');
		frm.set_value("appointment", '');
	},
});


const set_patient_encounter = (frm) => {
	if (!frm.doc.delivery_note) return;
	frappe.call({
		method: 'hms_tz.nhif.doctype.medication_change_request.medication_change_request.get_patient_encounter_name',
		async: false,
		args: {
			'delivery_note': frm.doc.delivery_note,
		},
		callback: function (data) {
			if (data.message) {
				frm.set_value("patient_encounter", data.message);
			}
			else {
				frm.set_value("patient_encounter", '');
			}
		}
	});
};

const set_delivery_note = (frm) => {
	if (!frm.doc.patient_encounter) return;
	frappe.call({
		method: 'hms_tz.nhif.doctype.medication_change_request.medication_change_request.get_delivery_note',
		async: false,
		args: {
			'patient_encounter': frm.doc.patient_encounter,
		},
		callback: function (data) {
			if (data.message) {
				frm.set_value("delivery_note", data.message);
			}
			else {
				frm.set_value("delivery_note", '');
			}
		}
	});
};

const update_childs_tables = (frm) => {
	frm.set_value("patient_encounter_final_diagnosis", []);
	frm.set_value("original_pharmacy_prescription", []);
	frm.set_value("drug_prescription", []);
	if (!frm.doc.patient_encounter) {
		return;
	}
	else {
		frappe.call({
			method: 'hms_tz.nhif.doctype.medication_change_request.medication_change_request.get_patient_encounter_doc',
			async: false,
			args: {
				'patient_encounter': frm.doc.patient_encounter,
			},
			callback: function (data) {
				if (data.message && data.message.name) {
					set_childs_tables(frm, data.message);
				}
			}
		});
	}
};

const set_childs_tables = (frm, doc) => {
	doc.patient_encounter_final_diagnosis.forEach(row => {
		row.name = null;
		frm.add_child('patient_encounter_final_diagnosis', row);
	});
	frm.refresh_field('patient_encounter_final_diagnosis');

	doc.drug_prescription.forEach(row => {
		row.name = null;
		frm.add_child('original_pharmacy_prescription', row);
		frm.add_child('drug_prescription', row);
	});
	frm.refresh_field('original_pharmacy_prescription');
	frm.refresh_field('drug_prescription');
};