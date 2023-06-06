frappe.ui.form.on('Therapy Plan', {
	setup: function(frm) {
		frm.get_field('therapy_plan_details').grid.editable_fields = [
			{fieldname: 'therapy_type', columns: 6},
			{fieldname: 'no_of_sessions', columns: 2},
			{fieldname: 'sessions_completed', columns: 2}
		];
	},
	
	refresh: function(frm) {
		if (!frm.doc.__islocal && (frm.doc.status == 'Not Serviced')) {
			frm.clear_custom_buttons();
			// frm.remove_custom_button("Create")
		}
		if (frm.doc.patient) {
			frm.add_custom_button(__('Patient History'), () => {
				frappe.route_options = { 'patient': frm.doc.patient };
				frappe.set_route('tz-patient-history');
			});
		}
	},
});