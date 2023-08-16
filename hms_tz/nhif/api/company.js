frappe.ui.form.on("Company", {
    refresh(frm) {
        frm.set_query("opd_cash_pharmacy", () => {
            return {
                filters: {
                    disabled: 0,
                    company: frm.doc.name,
                    service_unit_type: "Pharmacy",
                }
            }
        });
        frm.set_query("opd_insurance_pharmacy", () => {
            return {
                filters: {
                    disabled: 0,
                    company: frm.doc.name,
                    service_unit_type: "Pharmacy",
                }
            }
        });
        frm.set_query("ipd_cash_pharmacy", () => {
            return {
                filters: {
                    disabled: 0,
                    company: frm.doc.name,
                    service_unit_type: "Pharmacy",
                }
            }
        });
        frm.set_query("ipd_insurance_pharmacy", () => {
            return {
                filters: {
                    disabled: 0,
                    company: frm.doc.name,
                    service_unit_type: "Pharmacy",
                }
            }
        });
    }
});