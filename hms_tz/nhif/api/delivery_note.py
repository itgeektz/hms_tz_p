from __future__ import unicode_literals
import frappe
from frappe import _


def validate(doc, method):
    set_prescribed(doc)


def after_insert(doc, method):
    set_original_item(doc)


def set_original_item(doc):
    for item in doc.itmes:
        if item.item_code:
            item.original_item = item.item_code
            item.original_stock_uom_qty = item.stock_qty
    doc.save(ignore_permissions=True)


def onload(doc, method):
    for item in doc.items:
        if item.last_qty_prescribed:
            frappe.msgprint(
                _("The item {0} was last prescribed on {1} for {2} {3}").format(item.item_code, item.last_date_prescribed, item.last_qty_prescribed, item.stock_uom), alert=True)


def set_prescribed(doc):
    if doc.docstatus != 0:
        return

    for item in doc.items:
        items_list = frappe.db.sql("""
        select dn.posting_date, dni.item_code, dni.stock_qty, dni.uom from `tabDelivery Note` dn
        inner join `tabDelivery Note Item` dni on dni.parent = dn.name
                        where dni.item_code = %s
                        and dn.patient = %s
                        and dn.docstatus = 1
                        order by posting_date desc
                        limit 1""" %
                                   ('%s', '%s'), (item.item_code, doc.patient), as_dict=1)
        if len(items_list):
            item.last_qty_prescribed = items_list[0].get("stock_qty")
            item.last_date_prescribed = items_list[0].get("posting_date")
