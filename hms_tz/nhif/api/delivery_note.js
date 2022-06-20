frappe.ui.form.on("Delivery Note", {
    refresh: (frm) => {
        // hide button to delete rows of delivery note item
        $("*[data-fieldname='items']").find(".grid-add-row").hide();
        $("*[data-fieldname='items']").find(".grid-add-multiple-rows").hide();

        //hide button to delete rows of delivery note item
        $("*[data-fieldname='items']").find(".grid-remove-rows").hide();
        $("*[data-fieldname='items']").find(".grid-remove-all-rows").hide();
    },
});

frappe.ui.form.on("Delivery Note Item", {
    form_render: (frm, cdt, cdn) => {
        frm.fields_dict.items.grid.wrapper.find('.grid-delete-row').hide();
        frm.fields_dict.items.grid.wrapper.find('.grid-insert-row-below').hide();
        frm.fields_dict.items.grid.wrapper.find('.grid-insert-row').hide();
        frm.fields_dict.items.grid.wrapper.find('.grid-duplicate-row').hide();
        frm.fields_dict.items.grid.wrapper.find('.grid-move-row').hide();
        console.log("child form render");
    }
});