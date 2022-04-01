// Copyright (c) 2016, Aakvatech and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["Monthly NHIF Summary"] = {
	"filters": [
		{
			"fieldname": "submit_claim_month",
			"label": __("Submit Claim Month"),
			"fieldtype": "Int",
			"reqd": 1
		},
		{
			"fieldname": "submit_claim_year",
			"label": __("Submit Claim Year"),
			"fieldtype": "Int",
			"reqd": 1
		},
		{
			"fieldname": "company",
			"label": __("Company"),
			"fieldtype": "Link",
			"options": "Company",
			"reqd": 1
		}

	]
};
