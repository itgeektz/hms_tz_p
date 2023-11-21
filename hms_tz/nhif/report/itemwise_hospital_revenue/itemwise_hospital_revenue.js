// Copyright (c) 2023, Aakvatech and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["Itemwise Hospital Revenue"] = {
	"filters": [
		{
			"fieldname": "company",
			"label": __("Company"),
			"fieldtype": "Link",
			"options": "Company",
			"default": frappe.defaults.get_user_default("Company"),
			"reqd": 1,
			"on_change": function () {
				let company = frappe.query_report.get_filter_value('company');
				let payment_modes = frappe.query_report.get_filter('payment_mode');
				frappe.call({
					method: "hms_tz.nhif.report.itemwise_hospital_revenue.itemwise_hospital_revenue.get_payment_modes",
					args: {
						company: company
					},
					async: false,
					callback: function (r) {
						payment_modes.df.options = ''
						if (r.message && r.message.length > 0) {
							payment_modes.df.options = r.message;
						}
						payment_modes.refresh();
					}
				});
			}
		},
		{
			"fieldname": "from_date",
			"label": __("From Date"),
			"fieldtype": "Date",
			"reqd": 1,
			"on_change": function () {
				let company = frappe.query_report.get_filter_value('company');
				let payment_modes = frappe.query_report.get_filter('payment_mode');
				frappe.call({
					method: "hms_tz.nhif.report.itemwise_hospital_revenue.itemwise_hospital_revenue.get_payment_modes",
					args: {
						company: company
					},
					async: false,
					callback: function (r) {
						payment_modes.df.options = ''
						if (r.message && r.message.length > 0) {
							payment_modes.df.options = r.message;
						}
						payment_modes.refresh();
					}
				});
			}
		},
		{
			"fieldname": "to_date",
			"label": __("To Date"),
			"fieldtype": "Date",
			"reqd": 1,
		},
		{
			"fieldname": "service_type",
			"label": __("Service Type"),
			"fieldtype": "Link",
			"options": "Item Group",
		},
		{
			"fieldname": "payment_mode",
			"label": __("Payment Mode"),
			"fieldtype": "Select",
			"hidden": 0,
		},
		{
			"fieldname": "show_only_cancelled_items",
			"label": __("Show Only Cancelled Items"),
			"fieldtype": "Check",
			"on_change": function () {
				let show_only_cancelled = frappe.query_report.get_filter_value('show_only_cancelled_items');
				let bill_doctype = frappe.query_report.get_filter('bill_doctype');
				let service_type = frappe.query_report.get_filter('service_type');
				if (show_only_cancelled == 1) {
					bill_doctype.df.hidden = 0;
					service_type.df.hidden = 1;
					frappe.query_report.set_filter_value('payment_mode', '');
					frappe.query_report.set_filter_value('service_type', '');
					frappe.query_report.set_filter_value('bill_doctype', '');
				} else {
					bill_doctype.df.hidden = 1;
					service_type.df.hidden = 0;
					frappe.query_report.set_filter_value('payment_mode', '');
					frappe.query_report.set_filter_value('service_type', '');
					frappe.query_report.set_filter_value('bill_doctype', '');
				}
				bill_doctype.refresh();
				service_type.refresh();
			}
		},
		{
			"fieldname": "bill_doctype",
			"label": __("Bill Doctype"),
			"fieldtype": "Select",
			"options": "\nLab Test\nRadiology Examination\nClinical Procedure\nDelivery Note",
			"hidden": 1,
		},
	]
};