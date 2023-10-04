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
		},
		{
			"fieldname": "from_date",
			"label": __("From Date"),
			"fieldtype": "Date",
			"reqd": 1,
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
		}
	]
};