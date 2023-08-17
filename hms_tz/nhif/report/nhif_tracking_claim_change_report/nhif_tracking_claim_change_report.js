// Copyright (c) 2023, Aakvatech and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["NHIF Tracking Claim Change Report"] = {
	"filters": [
		{
			"fieldname": "company",
			"label": __("Company"),
			"fieldtype": "Link",
			"options": "Company NHIF Settings",
			"reqd": 1,
		},
		{
			"fieldname": "claim_month",
			"label": __("Claim Month"),
			"fieldtype": "Int",
			"reqd": 1,
		},
		{
			"fieldname": "claim_year",
			"label": __("Claim Year"),
			"fieldtype": "Int",
			"reqd": 1,
		},
		{
			"fieldname": "status",
			"label": __("Status"),
			"fieldtype": "Select",
			"options": ["", "Amount Changed", "Item Removed"],
		},
		{
			"fieldname": "nhif_patient_claim",
			"label": __("NHIF Patient Claim"),
			"fieldtype": "Link",
			"options": "NHIF Patient Claim",
		},
		{
			"fieldname": "edited_by",
			"label": __("Edited By"),
			"fieldtype": "Link",
			"options": "User",
			
		},
	],
	"formatter": (value, row, column, data, default_formatter) => {
		value = default_formatter(value, row, column, data);
		if (column.fieldname == 'status' && data[column.fieldname] == "Amount Changed") {
			value = `<span class='font-weight-bold text-info'>${value}</span>`;
		}
		if (column.fieldname == 'status' && data[column.fieldname] == "Item Removed") {
			value = `<span class='font-weight-bold text-danger'>${value}</span>`;
		}

		return value

	}
};
