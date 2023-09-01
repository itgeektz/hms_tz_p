frappe.ui.form.on('Inpatient Record', {
    reset_admission_status_to_admission_scheduled: function (frm) {
        frm.set_value("status", "Admission Scheduled")
        frm.refresh_fields("status")
        frm.save()
    },
    refresh(frm) {
        // hide button to delete rows of occupancy
        $('*[data-fieldname="inpatient_occupancies"]').find('.grid-remove-rows').hide();
        $('*[data-fieldname="inpatient_occupancies"]').find('.grid-remove-all-rows').hide();

        //hide button to delete rows of consultancy
        $('*[data-fieldname="inpatient_consultancy"]').find('.grid-remove-rows').hide();
        $('*[data-fieldname="inpatient_consultancy"]').find('.grid-remove-all-rows').hide();

        if (!frm.doc.insurance_subscription) {
            frm.add_custom_button(__("Create Invoice"), () => {
                create_sales_invoice(frm);
            });
            frm.add_custom_button(__("Make Deposit"), () => {
                make_deposit(frm);
            }).removeClass("btn-default").addClass("btn-warning font-weight-bold");
        }
    },
});

frappe.ui.form.on('Inpatient Occupancy', {
    form_render(frm, cdt, cdn) {
        frm.fields_dict.inpatient_occupancies.grid.wrapper.find('.grid-delete-row').hide();
        frm.fields_dict.inpatient_occupancies.grid.wrapper.find('.grid-duplicate-row').hide();
        frm.fields_dict.inpatient_occupancies.grid.wrapper.find('.grid-move-row').hide();
        frm.fields_dict.inpatient_occupancies.grid.wrapper.find('.grid-append-row').hide();
        frm.fields_dict.inpatient_occupancies.grid.wrapper.find('.grid-insert-row-below').hide();
        frm.fields_dict.inpatient_occupancies.grid.wrapper.find('.grid-insert-row').hide();
    },
    inpatient_occupancies_move: (frm, cdt, cdn) => {
        control_inpatient_record_move(frm, cdt, cdn);
    },
    confirmed: (frm, cdt, cdn) => {
        let row = frappe.get_doc(cdt, cdn);
        if (row.is_confirmed || !row.left) return;
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

const control_inpatient_record_move = (frm, cdt, cdn) => {
    let row = frappe.get_doc(cdt, cdn);
    frm.reload_doc();
    frappe.throw(__(`This line should not be moved`));

};

frappe.ui.form.on('Inpatient Consultancy', {
    form_render(frm, cdt, cdn) {
        frm.fields_dict.inpatient_consultancy.grid.wrapper.find('.grid-delete-row').hide();
        frm.fields_dict.inpatient_consultancy.grid.wrapper.find('.grid-duplicate-row').hide();
        frm.fields_dict.inpatient_consultancy.grid.wrapper.find('.grid-move-row').hide();
        frm.fields_dict.inpatient_consultancy.grid.wrapper.find('.grid-append-row').hide();
        frm.fields_dict.inpatient_consultancy.grid.wrapper.find('.grid-insert-row-below').hide();
        frm.fields_dict.inpatient_consultancy.grid.wrapper.find('.grid-insert-row').hide();
    },

    confirmed: (frm, cdt, cdn) => {
        let row = frappe.get_doc(cdt, cdn);
        if (row.is_confirmed) return;
        if (frm.is_dirty()) {
            frm.save();
        }
        frappe.model.set_value(cdt, cdn, "is_confirmed", 1);
        frm.refresh_field("inpatient_consultancy");
        frm.save();
    },
});

var make_deposit = (frm) => {
    frappe.prompt([
        {
            "fieldname": "deposit_amount",
            "fieldtype": "Currency",
            "label": "Deposit Amount",
            "description": "make sure you write the correct amount",
            "reqd": 1,
        },
        {
            "fieldname": "md_cb",
            "fieldtype": "Column Break",
        },
        {
            "fieldname": "mode_of_payment",
            "fieldtype": "Link",
            "label": "Mode of Payment",
            "options": "Mode of Payment",
            "reqd": 1,
        }
    ],

        (data) => {
            frappe.call({
                method: "hms_tz.nhif.api.inpatient_record.make_deposit",
                args: {
                    inpatient_record: frm.doc.name,
                    deposit_amount: data.deposit_amount,
                    mode_of_payment: data.mode_of_payment,
                },
                freeze: true,
                freeze_message: __('<i class="fa fa-spinner fa-spin fa-4x"></i>'),
            }).then((r) => {
                if (r.message) {
                    frm.reload_doc();
                }
            });
        },
        "Make Deposit",
        "Submit"
    );
}

var create_sales_invoice = (frm) => {
    frappe.prompt([
        {
            'fieldname': 'mode_of_payment',
            'fieldtype': 'Link',
            'label': 'Mode of Payment',
            'options': 'Mode of Payment',
            'reqd': 1
        }
    ],
        (values) => {
            let filters = {
                "patient": frm.doc.patient,
                "appointment_no": frm.doc.patient_appointment,
                "inpatient_record": frm.doc.name,
                "company": frm.doc.company,
                "mode_of_payment": values.mode_of_payment,
            }
            frappe.call({
                method: "hms_tz.nhif.api.inpatient_record.create_sales_invoice",
                args: {
                    args: filters
                },
                freeze: true,
                freeze_message: __('<i class="fa fa-spinner fa-spin fa-4x"></i>'),
            }).then((r) => {
                console.log(r.message)
                if (r.message) {
                    frappe.set_route("Form", "Sales Invoice", r.message);
                }
            });
        },
        "Create Sales Invoice",
        "Create"
    )
}
