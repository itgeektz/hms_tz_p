frappe.ui.form.on('Medical Department', {
    refresh: function(frm) {
        frm.set_query("main_department", function(){
            return {
                filters:[
                    ["Medical Department", "is_main", "=", 1]
                ]
            };
        });
    }
});