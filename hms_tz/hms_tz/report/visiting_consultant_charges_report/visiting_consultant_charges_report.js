// Copyright (c) 2022, Aakvatech and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["Visiting Consultant Charges Report"] = {
	"filters": [
		{
			"fieldname": "from_date",
			"fieldtype": "Date",
			"label": __("From Date"),
			'reqd': 1
		},
		{
			"fieldname": "to_date",
			"fieldtype": "Date",
			"label": __("To Date"),
			'reqd': 1
		},
		{
			"fieldname": "company",
			"fieldtype": "Link",
			"label": __("Company"),
			"options": "Company",
			'reqd': 1
		},
		{
			"fieldname": "practitioner",
			"fieldtype": "Link",
			"label": __("Healthcare Practitioner"),
			"options": "Healthcare Practitioner"
		},
		{
			"fieldname": "vc_technician",
			"fieldtype": "Link",
			"label": __("VC Technician"),
			"options": "User"
		}
	]
};
