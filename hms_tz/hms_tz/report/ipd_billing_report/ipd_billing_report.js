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
		}
	]
};
