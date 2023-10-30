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
			"options": ["", "Open", "Closed", "Scheduled", "Cancelled"],
			"default": "",
			"reqd": 0,
		},
		{
			"fieldname": "patient_type",
			"fieldtype": "Select",
			"label": __("Patient Type"),
			"options": ["", "In-patient", "Out-patient"],
			"default": "",
			"reqd": 0,
		}
	],
	'formatter': (value, row, column, data, default_formatter) => {
		value = default_formatter(value, row, column, data);
		
		if ((data.nhif_patient_claim != '' && data.nhif_patient_claim != null) && (data.signature == '' || data.signature == null)) {
			value = `<span style='color:red'>${data[column.fieldname]}</span>`;
		}
		if (data.repeated_auth_no && data.repeated_auth_no == true && column.fieldname == 'authorization_number') {
			value = `<span style='color:blue'>${value}</span>`;

			const $tempDiv = $('<div></div>').html(value);
			const $spanElement = $tempDiv.find('span');
			if ($spanElement.length > 0) {
				$spanElement.css('color', '').css('color', 'blue');
			}
	
			value = $tempDiv.html();
		}
		["inpatient_record", "inpatient_status", "signature"].forEach((field) => { 
			if ((data[field] == null || data[field] == '') && column.fieldname == field) {
				value = '';
			}
		});

		return value
	}
};