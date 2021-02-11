from __future__ import unicode_literals
import frappe
from frappe import _


def validate(doc, method):
    set_prescribed(doc)


def onload(doc, method):
    set_prescribed(doc)


def set_prescribed(doc):
    if doc.docstatus != 0:
        return
    note_list_names = []
    note_list = frappe.get_all("Delivery Note", filtes={
        "docstatus": 1, "patient": doc.patient}, order_by='posting_date desc')
    for note in note_list:
        note_list_names.append(note.name)
    for item in doc.items:
        items_list = frappe.get_all("Delivery Note Item", filtes={
            "parent": ['in', note_list_names], "item_code": item.item_code}, fields=["qty", "uom", "parent"], order_by='modified desc')
        if len(items_list):
            item.last_qty_prescribed = items_list[0].qty
            item.last_date_prescribed = frappe.get_value(
                "Delivery Note", items_list[0].parent, "posting_date")
