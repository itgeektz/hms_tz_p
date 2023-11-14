// Copyright (c) 2020, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt

frappe.ui.form.on('Healthcare Insurance Coverage Plan', {
	refresh: function(frm) {
        frm.set_query("opd_insurance_pharmacy", () => {
            return {
                filters: {
                    disabled: 0,
                    company: frm.doc.company,
                    service_unit_type: "Pharmacy",
                }
            }
		});
        frm.set_query("ipd_insurance_pharmacy", () => {
            return {
                filters: {
                    disabled: 0,
                    company: frm.doc.company,
                    service_unit_type: "Pharmacy",
                }
            }
        });
	},
	insurance_company: function(frm){
		if(frm.doc.insurance_company){
			frappe.call({
				'method': 'frappe.client.get_value',
				args: {
					doctype: 'Healthcare Insurance Contract',
					filters: {
						'insurance_company': frm.doc.insurance_company,
						'is_active':1,
						'end_date':['>=', frappe.datetime.nowdate()],
						'docstatus':1
					},
					fieldname: ['name']
				},
				callback: function (data) {
					if(!data.message.name){
						frappe.msgprint(__('There is no valid contract with this Insurance Company {0}',[frm.doc.insurance_company]));
						frm.set_value('insurance_company', '');
						frm.set_value('insurance_company_name', '');
					}
				}
			});
		}
	},
});
