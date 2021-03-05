frappe.ui.form.on('Inpatient Record', {

});

frappe.ui.form.on('Inpatient Occupancy', {
    confirmed: (frm, cdt, cdn) => {
        let row = frappe.get_doc(cdt, cdn);
        if (row.invoiced || !row.left) return;
        if (frm.is_dirty()) {
            frm.save();
        }
        frappe.call({
            method: 'hms_tz.nhif.api.inpatient_record.confirmed',
            args: {
                row: row,
                doc: frm.doc
            },
            callback: function (data) {
                if (data.message) {

                }
                frm.reload_doc();
            }
        });

    }
});