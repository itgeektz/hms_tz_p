// Copyright (c) 2022, Aakvatech and contributors
// For license information, please see license.txt

frappe.ui.form.on('NHIF Custom Excluded Services', {
	refresh: function (frm) {
		frm.set_query('item', () => {
			return {
				filters: {
					disabled: 0
				}
			}
		});

		frm.trigger('item');
	},

	item: (frm) => {
		if (frm.doc.company && frm.doc.item && frm.is_new()) {
			frappe.call('hms_tz.nhif.doctype.nhif_custom_excluded_services.nhif_custom_excluded_services.validate_item', {
				company: frm.doc.company, item: frm.doc.item, name: frm.doc.name
			}).then((r) => {
				if (r.message.length > 0) {
					frappe.set_route("FORM", "NHIF Custom Excluded Services", r.message);
					frappe.msgprint(__(`<p>Item: <b>${__(frm.doc.item)}</b> already exists for 
							company: <b>${__(frm.doc.company)}</b> on docname: <b>${__(r.message)}</b></p>`)
					);
				}
			});
		}
	}
});
