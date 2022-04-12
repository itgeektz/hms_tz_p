// Copyright (c) 2022, Aakvatech and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["Itemized Bill Report"] = {
	filters: [
		{
			fieldname: "patient",
			label: __("Patient"),
			fieldtype: "Link",
			options: "Patient",
			reqd: 1,
		},
		{
			fieldname: "patient_appointment",
			label: __("Patient Appointment"),
			fieldtype: "Link",
			options: "Patient Appointment",
			reqd: 1,
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
	],
};
