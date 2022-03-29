frappe.ui.form.on('Clinical Procedure', {
    refresh: function(frm) {
        frm.remove_custom_button('Start');
        frm.remove_custom_button('Complete');
    },

    onload: function(frm) {
        frm.remove_custom_button('Start');
        frm.remove_custom_button('Complete');
    }
})