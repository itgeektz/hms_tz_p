// Copyright (c) 2016, Aakvatech and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["IPD Billing Report"] = {
	onload: (report) => {
		report.page.add_inner_button(__("Make Deposit"), () => {
			let filters = report.get_values();
			make_deposit(filters.inpatient_record);
		}).removeClass("btn-default").addClass("btn-warning font-weight-bold");
	},

	"filters": [
		{
			"fieldname": "inpatient_record", 
			"fieldtype": "Link",
			"label": __("Inpatient Record"), 
			"options": "Inpatient Record",
			"reqd": 1
		},
		{
			"fieldname": "patient", 
			"fieldtype": "Link",
			"label": __("Patient"), 
			"options": "Patient",
			"reqd": 1
		},
		{
			"fieldname": "appointment_no",
			"fieldtype": "Data",
			"label": __("AppointmentNo"),
			"reqd": 1
		},
		{
			"fieldname": "company", 
			"fieldtype": "Link", 
			"label": __("Company"),
			"options": "Company",
			"reqd": 1
		},
		{
			fieldname: 'patient_type',
			label: __('Patient Type'),
			fieldtype: 'Select',
			options: ["", 'Out-Patient', 'In-Patient'],
			reqd: 0,
		},
		{
			fieldname: "from_date",
			label: __("From Date"),
			fieldtype: "Date",
			reqd: 0,
		},
		{
			fieldname: "to_date",
			label: __("To Date"),
			fieldtype: "Date",
			reqd: 0,
		},
		{
			"fieldname": "summarized_view", 
			"fieldtype": "Check", 
			"label": __("Summarized View")
		},
	],
	'formatter': (value, row, column, data, default_formatter) => {
		value = default_formatter(value, row, column, data);
		if (column.fieldtype == 'Currency' && data[column.fieldname] > 0) {
			value = `<span class='font-weight-bold text-secondary'>${value}</span>`;
		}
		if (column.fieldtype == 'Currency' && data[column.fieldname] == 0) {
			value = `<span class='text-warning'>${value}</span>`;
		}
		if (data && row[1].content == 'Total') {
			value = $(`<span>${value}</span>`);
			var $value = $(value).css("font-weight", "bold");
			value = $value.wrap("<p></p>").parent().html();
		}
		return value
	}
};

var make_deposit = (inpatient_record) => {
	frappe.prompt([
		{
			"fieldname": "deposit_amount",
			"fieldtype": "Currency",
			"label": "Deposit Amount",
			"description": "make sure you write the correct amount",
			"reqd": 1,
		},
		{
			"fieldname": "md_cb",
			"fieldtype": "Column Break",
		},
		{
			"fieldname": "mode_of_payment",
			"fieldtype": "Link",
			"label": "Mode of Payment",
			"options": "Mode of Payment",
			"reqd": 1,
		}
	],

		(data) => {
			frappe.dom.freeze(__("Making Deposit..."));
			frappe.call({
				method: "hms_tz.nhif.api.inpatient_record.make_deposit",
				args: {
					inpatient_record: inpatient_record,
					deposit_amount: data.deposit_amount,
					mode_of_payment: data.mode_of_payment,
				},
			}).then((r) => {
				frappe.dom.unfreeze();
				if (r.message) {
					frm.reload_doc();
				}
			});
		},
		"Make Deposit",
		"Submit"
	);
}
