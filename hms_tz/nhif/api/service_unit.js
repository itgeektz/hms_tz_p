frappe.ui.form.on('Healthcare Service Unit', {
    refresh: (frm) => {
        frm.set_query('warehouse', function () {
            return {
                filters: [
                    ["Warehouse","company", "=", frm.doc.company]
                ]
            };
        });
        
        frm.set_query("department", function(){
            return {
                filters: [
                    ["Department","company", "=", frm.doc.company]
                ]
            }
        });
    }
})