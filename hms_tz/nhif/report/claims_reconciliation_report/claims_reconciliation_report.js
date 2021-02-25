// Copyright (c) 2016, Aakvatech and contributors
// For license information, please see license.txt
/* eslint-disable */

const getYears = () => {
	let years = "";
	const currentYear = new Date().getFullYear();
	let i = 0;
	while (i < 10) {
		years += (parseInt(currentYear) - i) + '\n';
		i++;
	}
	return years.slice(0, -1);
};


frappe.query_reports["Claims Reconciliation Report"] = {
	"filters": [
		{
			"fieldname": "company",
			"label": __("Company"),
			"fieldtype": "Link",
			"options": "Company",
			"reqd": 1,
			"default": frappe.defaults.get_user_default("company")
		},
		{
			"fieldname": "ClaimYear",
			"label": __("ClaimYear"),
			"fieldtype": "Select",
			"default": new Date().getFullYear(),
			"options": getYears(),
			"reqd": 1,
			"width": "30px"
		},
		{
			"fieldname": "ClaimMonth",
			"label": __("Claim Month"),
			"fieldtype": "Select",
			"default": 1,
			"options": '1\n2\n3\n4\n5\n6\n7\n8\n9\n10\n11\n12',
			"reqd": 1,
			"width": "30px"
		},
	]
};
