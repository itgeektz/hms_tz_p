// Copyright (c) 2022, Aakvatech and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["NHIF Patient Tracking Report"] = {
	"filters": [
		{
            "fieldname": "from_date",
            "label": __("From Date"),
            "fieldtype": "Date",
            "reqd": 1
        },
        {
            "fieldname": "to_date",
            "label": __("To Date"),
            "fieldtype": "Date",
            "reqd": 1
        },
		{
			"fieldname": "company",
			"label": __("Company"),
			"fieldtype": "Link",
			"options": "Company",
			"default": frappe.defaults.get_user_default("Company"),
			"reqd": 1
		},
		{
			"fieldname": "status",
			"fieldtype": "Select",
			"label": __("Status"),
			"options": ["", "Open", "Closed"],
			"default": "",
			"reqd": 0,
		}
	],
	'formatter': (value, row, column, data, default_formatter) => {
		value = default_formatter(value, row, column, data);
		
		if (data.nhif_claim_no != '' && data.signature == '') {
			value = `<div style='color:red'>${data[column.fieldname]}</div>`;
		}

		return value
	}
};