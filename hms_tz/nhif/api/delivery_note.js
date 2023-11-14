frappe.ui.form.on("Delivery Note", {
    refresh(frm) {
        $('[data-label="Not%20Serviced"]').parent().hide();
        $('[data-label="Request%20Changes"]').parent().hide();
        $('[data-label="Make%20Changes"]').parent().hide();
        $('[data-label="Issue%20Returns"]').parent().hide();
        $('[data-label="Return"]').parent().hide();
        
        if (!frappe.user.has_role("DN Changed Allowed")) {
            // hide button to add rows of delivery note item
            frm.get_field("items").grid.cannot_add_rows = true;

            // hide button to delete rows of delivery note item
            $("*[data-fieldname='items']").find(".grid-remove-rows").hide();
            $("*[data-fieldname='items']").find(".grid-remove-all-rows").hide();
        }
    },
    onload(frm){
        $('[data-label="Not%20Serviced"]').parent().hide();
        $('[data-label="Request%20Changes"]').parent().hide();
        $('[data-label="Make%20Changes"]').parent().hide();
        $('[data-label="Issue%20Returns"]').parent().hide();
        $('[data-label="Return"]').parent().hide();

        if (!frappe.user.has_role("DN Changed Allowed")) {
            // hide button to add rows of delivery note item
            frm.get_field("items").grid.cannot_add_rows = true;

            // hide button to delete rows of delivery note item
            $("*[data-fieldname='items']").find(".grid-remove-rows").hide();
            $("*[data-fieldname='items']").find(".grid-remove-all-rows").hide();
        }
    },
    hms_tz_lrpmt_returns: (frm) => {
        frappe.call({
            method: "hms_tz.nhif.api.healthcare_utils.return_quatity_or_cancel_delivery_note_via_lrpmt_returns",
            args: {
                source_doc: frm.doc,
                method: "From Front End"
            },
            freeze: true,
            callback: (r) => {
                if (r.message == true) {
                    frm.refresh()
                } else {
                    frappe.set_route("FORM", "LRPMT Returns", r.message);
                }
            },
        })
    },
    hms_tz_medicatiion_change_request: (frm) => {
        if (!frm.doc.hms_tz_comment) {
            frappe.msgprint("<b>Please write an item(s) to be changed on the comment field</b>");
            return 
        }
        frappe.call({
            method: "hms_tz.nhif.doctype.medication_change_request.medication_change_request.create_medication_change_request_from_dn",
            args: {
                doctype: frm.doc.doctype,
                name: frm.doc.name
            },
            freeze: true,
            callback: (r) => {
            },
        });
    }
});

frappe.ui.form.on("Delivery Note Item", {
    form_render: (frm, cdt, cdn) => {
        if (!frappe.user.has_role("DN Changed Allowed")) {
            frm.fields_dict.items.grid.wrapper.find('.grid-delete-row').hide();
            frm.fields_dict.items.grid.wrapper.find('.grid-insert-row-below').hide();
            frm.fields_dict.items.grid.wrapper.find('.grid-insert-row').hide();
            frm.fields_dict.items.grid.wrapper.find('.grid-duplicate-row').hide();
            frm.fields_dict.items.grid.wrapper.find('.grid-move-row').hide();
        }
    },
    approval_number: (frm, cdt, cdn) => {
        let row = locals[cdt][cdn]
        if (row.approval_number != "" && row.approval_number != undefined) {
            if (!frm.doc.customer.includes("NHIF")) {
                return;
            }
            frappe.call({
                method: "hms_tz.nhif.api.healthcare_utils.varify_service_approval_number_for_LRPM",
                args: {
                    company: frm.doc.company,
                    approval_number: row.approval_number,
                    template_doctype: "Medication",
                    template_name: row.item_code,
                    encounter: frm.doc.reference_name
                },
                freeze: true,
                freeze_message: __('<i class="fa fa-spinner fa-spin fa-4x"></i>'),
            }).then(r => {
                if (r.message && r.message == "approval number validation is disabled") {
                        return
                    }
                else if (r.message) {
                    frappe.show_alert({
                        message: __("<h4 class='text-center' style='background-color: #D3D3D3; font-weight: bold;'>\
                            Approval Number is Valid</h4>"),
                        indicator: "green"
                    }, 20);
                } else {
                    row.approval_number = ""
                    frappe.show_alert({
                        message: __("<h4 class='text-center' style='background-color: #D3D3D3; font-weight: bold;'>\
                            Approval Number is not Valid</h4>"),
                        indicator: "Red"
                    }, 20);
                }
            });
        }
    }
});

frappe.ui.form.on("Original Delivery Note Item", {
    form_render: (frm, cdt, cdn) => {
        if (frm.doc.hms_tz_all_items_out_of_stock == 1) {
            frm.fields_dict.hms_tz_original_items.grid.wrapper.find('[data-fieldname="convert_to_in_stock_item"]').hide();
        }
        if (locals[cdt][cdn].hms_tz_is_out_of_stock == 0) {
            frm.fields_dict.hms_tz_original_items.grid.wrapper.find('[data-fieldname="convert_to_in_stock_item"]').hide();
        }
    },
    
    convert_to_in_stock_item: (frm, cdt, cdn) => {
        let original_row = frappe.get_doc(cdt, cdn);

        if (original_row.hms_tz_is_out_of_stock == 1) {
            frappe.call('hms_tz.nhif.api.delivery_note.convert_to_instock_item', {
                name: frm.doc.name, row: original_row
            }).then(r => {
                if (r.message) {
                    frm.reload_doc();
                }
            });
        } else {
            frappe.msgprint('This Item is not out of stock');
        }
    }
});
