frappe.ui.form.on('Inpatient Record', {

});

frappe.ui.form.on('Inpatient Occupancy', {
    before_inpatient_occupancies_remove: (frm, cdt, cdn) => {
        control_inpatient_record_permissing(frm, cdt, cdn);
    },
    before_inpatient_occupancies_remove_all: (frm, cdt, cdn) => {
        control_inpatient_record_permissing(frm, cdt, cdn);
    },
    inpatient_occupancies_add: (frm, cdt, cdn) => {
        control_inpatient_record_permissing(frm, cdt, cdn);
    },
    inpatient_occupancies_remove: (frm, cdt, cdn) => {
        control_inpatient_record_permissing(frm, cdt, cdn);
    },
    inpatient_occupancies_move: (frm, cdt, cdn) => {
        control_inpatient_record_move(frm, cdt, cdn);
    },
    check_in: (frm, cdt, cdn) => {
        control_inpatient_record_permissing(frm, cdt, cdn);
    },
    check_out: (frm, cdt, cdn) => {
        control_inpatient_record_permissing(frm, cdt, cdn);
    },
    invoiced: (frm, cdt, cdn) => {
        control_inpatient_record_permissing(frm, cdt, cdn);
    },
    service_unit: (frm, cdt, cdn) => {
        control_inpatient_record_permissing(frm, cdt, cdn);
    },
    left: (frm, cdt, cdn) => {
        control_inpatient_record_permissing(frm, cdt, cdn);
    },
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
    },
});

const control_inpatient_record_permissing = (frm, cdt, cdn) => {
    // let row = frappe.get_doc(cdt, cdn);
    // if (row.invoiced) {
    //     frm.reload_doc();
    //     frappe.throw(__(`This line has been invoiced. It cannot be modified or deleted`));
    // }
};

const control_inpatient_record_move = (frm, cdt, cdn) => {
    let row = frappe.get_doc(cdt, cdn);
    frm.reload_doc();
    frappe.throw(__(`This line should not be moved`));

};