// Copyright (c) 2023, Aakvatech and contributors
// For license information, please see license.txt

frappe.ui.form.on('Healthcare Package', {
	refresh: function (frm) {
		frm.set_query("price_list", () => {
			return {
				filters: {
					enabled: 1,
					selling: 1
				}
			};
		})

		if (frm.doc.disabled == 1) {
			frm.disable_form();
		}
	},

	onload: (frm) => {
		frm.set_total_actual_item_price = (frm, row) => {
			let total = 0;
			frm.doc.services.forEach((row) => {
				total += row.actual_item_price;
			});
			frm.doc.consultations.forEach((row) => {
				total += row.actual_item_price;
			});
			console.log(total)
			frm.set_value("total_actual_item_price", total);
		}

		frm.set_total_service_prices = (frm, row) => {
			let total_service_price = 0;
			frm.doc.services.forEach((row) => {
				total_service_price += row.service_price;
			});
			frm.doc.consultations.forEach((row) => {
				total_service_price += row.service_price;
			});
			frm.set_value("total_price_of_services", total_service_price);

		}
	},
});

frappe.ui.form.on('Healthcare Package Item', {
	services_add: (frm, cdt, cdn) => {
		frappe.model.set_value(cdt, cdn, "price_list", frm.doc.price_list);
	},
	healthcare_service: (frm, cdt, cdn) => {
		let row = frappe.get_doc(cdt, cdn);
		if (row.healthcare_service && row.price_list) {
			get_item_price(frm, row, row.healthcare_service_type, row.healthcare_service, row.price_list);
		}
	},
	price_list: (frm, cdt, cdn) => {
		let row = frappe.get_doc(cdt, cdn);
		if (row.healthcare_service && row.price_list) {
			get_item_price(frm, row, row.healthcare_service_type, row.healthcare_service, row.price_list);
		}
	},
	actual_item_price: (frm, cdt, cdn) => {
		let row = frappe.get_doc(cdt, cdn);
		frm.set_total_actual_item_price(frm, row);
	},
	service_price: (frm, cdt, cdn) => {
		let row = frappe.get_doc(cdt, cdn);
		frm.set_total_service_prices(frm, row);
	}

});

frappe.ui.form.on('Healthcare Package Consultation', {
	consultations_add: (frm, cdt, cdn) => {
		frappe.model.set_value(cdt, cdn, "price_list", frm.doc.price_list);
	},
	consultation_item: (frm, cdt, cdn) => {
		let row = frappe.get_doc(cdt, cdn);
		if (row.consultation_item && row.price_list) {
			get_item_price(frm, row, "Item", row.consultation_item, row.price_list, row.consultation_item);
		}
	},
	price_list: (frm, cdt, cdn) => {
		let row = frappe.get_doc(cdt, cdn);
		if (row.consultation_item && row.price_list) {
			get_item_price(frm, row, "Item", row.consultation_item, row.price_list, row.consultation_item);
		}
	},
	actual_item_price: (frm, cdt, cdn) => {
		let row = frappe.get_doc(cdt, cdn);
		frm.set_total_actual_item_price(frm, row);
	},
	service_price: (frm, cdt, cdn) => {
		let row = frappe.get_doc(cdt, cdn);
		frm.set_total_service_prices(frm, row);
	}
});

var get_item_price = (frm, row, healthcare_service_type, healthcare_service, price_list, item_code = null) => {
	frappe.call({
		method: "hms_tz.nhif.doctype.healthcare_package.healthcare_package.get_item_price",
		args: {
			template_type: healthcare_service_type,
			template: healthcare_service,
			price_list: price_list,
			item_code: item_code
		},
		callback: (r) => {
			if (r.message) {
				frappe.model.set_value(row.doctype, row.name, "actual_item_price", r.message);
			}
		}
	});
}