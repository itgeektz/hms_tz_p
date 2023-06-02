// Copyright (c) 2016, Aakvatech and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["IPD Billing Report"] = {
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
