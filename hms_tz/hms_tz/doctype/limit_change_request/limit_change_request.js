// Copyright (c) 2021, Aakvatech and contributors
// For license information, please see license.txt

frappe.ui.form.on('Limit Change Request', {
    refresh: function (frm) {
        frm.fields_dict.appointment_no.get_query = function () {
            return {
                query: 'hms_tz.hms_tz.utils.get_closed_appointments',
                filters: {
                    "patient": frm.doc.patient
                }
            };
        };
    }
});

