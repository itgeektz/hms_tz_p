frappe.ui.form.on('Healthcare Insurance Company', {
    onload: function (frm) {
        add_get_price_btn(frm)
    },
    refresh: function (frm) {
        add_get_price_btn(frm)
    },
});

var add_get_price_btn = function (frm) {
    if (!frm.doc.insurance_company_name.includes("NHIF")) { return }
    frm.add_custom_button(__('Get NHIF Price Package'), function () {
        frappe.call({
            method: 'hms_tz.nhif.api.insurance_company.enqueue_get_nhif_price_package',
            args: { company: frm.doc.company },
            callback: function (data) {
                if (data.message) {
                    console.log(data.message)
                }
            }
        });
    });
    if (!frm.doc.insurance_company_name.includes("NHIF")) { return }
    frm.add_custom_button(__('Only Process NHIF Records'), function () {
        frappe.call({
            method: 'hms_tz.nhif.api.insurance_company.process_nhif_records',
            args: { company: frm.doc.company },
            callback: function (data) {
                if (data.message) {
                    console.log(data.message)
                }
            }
        });
    });

}