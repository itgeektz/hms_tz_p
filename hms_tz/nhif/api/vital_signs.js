frappe.ui.form.on('Vital Signs', {
    height_in_cm: function (frm) {
        frm.set_value("height", frm.doc.height_in_cm / 100)
    },
})