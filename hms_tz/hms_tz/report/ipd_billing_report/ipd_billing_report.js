// Copyright (c) 2016, Aakvatech and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["IPD Billing Report"] = {
	onload: (report) => {
		report.page.add_inner_button(__("Make Deposit"), () => {
			let filters = report.get_values();
			make_deposit(filters.inpatient_record);
		}).addClass("font-weight-bold");
	},

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
			// options: ["", 'Out-Patient', 'In-Patient'],
			options: ['In-Patient'],
			default: 'In-Patient',
			reqd: 1,
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

var make_deposit = (inpatient_record) => {
    let d = new frappe.ui.Dialog({
        title: "Patient Deposit",
        fields: [
            {
                label: "Deposit Amount",
                fieldname: "deposit_amount",
                fieldtype: "Currency",
                description: "make sure you write the correct amount",
                reqd: 1,
            },
            {
                label: "Reference Number",
                fieldname: "reference_number",
                fieldtype: "Data",
            },
            {
                fieldname: "md_cb",
                fieldtype: "Column Break"
            },
            {
                label: "Mode of Payment",
                fieldname: "mode_of_payment",
                fieldtype: "Link",
                options: "Mode of Payment",
                reqd: 1,
                "description": "make sure you select the correct mode of payment",
            },
            {
                fieldname: "reference_date",
                fieldtype: "Date",
                label: "Reference Date",
            }
        ],
        size: "large", // small, large, extra-large 
        primary_action_label: 'Submit',
        primary_action(values) {
            console.log(values);
            frappe.call({
                method: "frappe.client.get_value",
                args: {
                    doctype: "Mode of Payment",
                    filters: { name: values.mode_of_payment },
                    fieldname: ["type"]
                },
            }).then((r) => {
                if (r.message) {
                    if (r.message.type != "Cash" && !values.reference_number) {
                        frappe.msgprint({
                            title: __("Reference Number is required"),
                            indicator: 'red',
                            message: __("Reference Number is required for non cash payments,<br>please enter reference number or change mode of payment to cash")
                        })
                    } else if (r.message.type != "Cash" && !values.reference_date) {
                        frappe.msgprint({
                            title: __("Reference Date is required"),
                            indicator: 'red',
                            message: __("Reference Date is required for non cash payments,<br>please enter reference date or change mode of payment to cash")
                        })
                    } else {
                        d.hide();
                        frappe.call({
                            method: "hms_tz.nhif.api.inpatient_record.make_deposit",
                            args: {
                                inpatient_record: inpatient_record,
                                deposit_amount: values.deposit_amount,
                                mode_of_payment: values.mode_of_payment,
                                reference_number: values.reference_number,
                                reference_date: values.reference_date,
                            },
                            freeze: true,
                            freeze_message: __('<i class="fa fa-spinner fa-spin fa-4x"></i>'),
                        }).then((r) => {
                            if (r.message) {
                                frm.reload_doc();
                            }
                        });
                    }
                }
            });
        }
    });

    d.show();
}