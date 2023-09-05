// Copyright (c) 2023, Aakvatech and contributors
// For license information, please see license.txt

frappe.ui.form.on('Healthcare Package Order', {
	refresh: (frm) => {
		frm.get_field("consultations").grid.cannot_add_rows = true;
		frm.get_field("consultations").$wrapper.find(".grid-remove-rows").hide();
		frm.get_field("consultations").$wrapper.find(".grid-remove-all-rows").hide();

		if (frm.doc.create_sales_invoice) {
			frm.set_df_property("payment_type", "read_only", 1);
			frm.set_df_property("mode_of_payment", "read_only", 1);
		}
		frm.set_query('insurance_subscription', function () {
			return {
				filters: {
					"is_active": 1,
					"docstatus": 1,
					"insurance_company": ["not like", "NHIF"],
					"patient": frm.doc.patient
				}
			};
		});
	},
	onload: (frm) => {
		frm.get_field("consultations").grid.cannot_add_rows = true
		frm.get_field("consultations").$wrapper.find(".grid-remove-rows").hide();
		frm.get_field("consultations").$wrapper.find(".grid-remove-all-rows").hide();
		if (frm.doc.create_sales_invoice) {
			frm.set_df_property("payment_type", "read_only", 1);
			frm.set_df_property("mode_of_payment", "read_only", 1);
		}
		frm.set_query('insurance_subscription', function () {
			return {
				filters: {
					'is_active': 1,
					'docstatus': 1,
					'patient': frm.doc.patient
				}
			};
		});
	},
	healthcare_package: (frm) => {
		if (frm.doc.healthcare_package) {
			frappe.db.get_doc("Healthcare Package", frm.doc.healthcare_package)
				.then((package_doc) => {
					show_package_items(frm, package_doc);

					frm.clear_table("consultations");
					package_doc.consultations.forEach((row) => {
						let child = frm.add_child("consultations", {
							"consultation_item": row.consultation_item,
							// "consultation_fee": row.service_price,
						});
					});
					frm.refresh_field("consultations");
				});
		} else {
			frm.get_field("package_items").html("");
			frm.clear_table("consultations");
		}
	},
	payment_type: (frm) => {
		if (frm.doc.payment_type == "Insurance") {
			frm.set_value("mode_of_payment", null);
		}
		if (frm.doc.payment_type == "Cash") {
			frm.set_value("insurance_subscription", null);
		}
	},
	create_sales_invoice: (frm) => {
		if (frm.is_dirty()) {
			frappe.msgprint(__("<b>Please save the document before creating Sales Invoice</b>"));
			return;
		}

		frm.call("create_sales_invoice", {
			self: frm.doc,
			freeze: true,
			freeze_message: __('<i class="fa fa-spinner fa-spin fa-4x"></i>'),
		}).then((r) => {
			if (r.message) {
				frm.set_df_property("payment_type", "read_only", 1);
				frm.set_df_property("mode_of_payment", "read_only", 1);
				frm.refresh();
			}
		});
	}
});

frappe.ui.form.on('Healthcare Package Order Consultation', {
	form_render: (frm, cdt, cdn) => {
		frm.get_field("consultations").grid.wrapper.find(".grid-delete-row").hide();
		frm.get_field("consultations").grid.wrapper.find(".grid-move-row").hide();
		frm.get_field("consultations").grid.wrapper.find(".grid-duplicate-row").hide();
		frm.get_field("consultations").grid.wrapper.find(".grid-append-row").hide();
		frm.get_field("consultations").grid.wrapper.find(".grid-insert-row").hide();
		frm.get_field("consultations").grid.wrapper.find(".grid-insert-row-below").hide();
	},
});

let show_package_items = (frm, package_doc) => {
	let html = ``;
	if (package_doc.services.length > 0) {
		html += `<style>
					.table {border-collapse: collapse; width: 100%;}
					.table th, .table td {border: 1px solid #dddddd; padding: 8px; text-align: left;}
					.table th {background-color: #f2f2f2;}
					.table tbody tr:nth-child(even) {background-color: #f9f9f9;}
					.table tbody tr:hover {background-color: #eaeaea;}
				</style>
		
				<table class="table table-sm table-bordered">
				<thead>
					<tr>
						<th>Healthcare Service Type</th>
						<th>Healthcare Service</th>
					</tr>
				</thead>
				<tbody>`;
		// <th>Service Price</th>

		if (package_doc.consultations.length > 0) {
			package_doc.consultations.forEach((row) => {
				html += `<tr>
					<td style="border: 1px solid #dddddd; padding: 8px;">Consultation</td>
					<td style="border: 1px solid #dddddd; padding: 8px;">${row.consultation_item}</td>
					
				</tr>`;
				// <td class="text-right" style="border: 1px solid #dddddd; padding: 8px;">
				// 	${frappe.format(row.service_price, { fieldtype: "Currency", options: "currency" })}
				// </td>
			});
		}

		if (package_doc.services.length > 0) {
			package_doc.services.forEach((row) => {
				html += `<tr>
					<td style="border: 1px solid #dddddd; padding: 8px;">${row.healthcare_service_type}</td>
					<td style="border: 1px solid #dddddd; padding: 8px;">${row.healthcare_service}</td>
				</tr>`;
				// <td class="text-right" style="border: 1px solid #dddddd; padding: 8px;">
				// 	${frappe.format(row.service_price, { fieldtype: "Currency", options: "currency" })}
				// </td>
			});
		}
		html += `</tbody></table>`;
	}

	frm.get_field("package_items").html(html);
}