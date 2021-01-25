import frappe
from frappe import _


@frappe.whitelist()
@frappe.validate_and_sanitize_search_inputs
def get_practitioner_list(doctype, txt, searchfield, start, page_len, filters=None):
    frappe.throw(str(doctype))
    fields = searchfield + ['name', 'practitioner_name']

    # filters.update({
    #     'name': ('like', '%%%s%%' % txt)
    # })

    return frappe.get_all('Healthcare Practitioner', fields=fields,
                          filters=filters, start=start, page_length=page_len, order_by='name, practitioner_name', as_list=1)
