from __future__ import unicode_literals
import frappe
from frappe import _
from hms_tz.nhif.api.healthcare_utils import update_dimensions


def validate(doc, method):
    set_prescribed(doc)
    set_missing_values(doc)
    update_dimensions(doc)


def after_insert(doc, method):
    set_original_item(doc)


def set_original_item(doc):
    for item in doc.items:
        if item.item_code:
            item.original_item = item.item_code
            item.original_stock_uom_qty = item.stock_qty
    doc.save(ignore_permissions=True)


def onload(doc, method):
    for item in doc.items:
        if item.last_qty_prescribed:
            frappe.msgprint(
                _("The item {0} was last prescribed on {1} for {2} {3}").format(
                    item.item_code,
                    item.last_date_prescribed,
                    item.last_qty_prescribed,
                    item.stock_uom,
                ),
            )


def set_prescribed(doc):
    if doc.docstatus != 0:
        return

    for item in doc.items:
        items_list = frappe.db.sql(
            """
        select dn.posting_date, dni.item_code, dni.stock_qty, dni.uom from `tabDelivery Note` dn
        inner join `tabDelivery Note Item` dni on dni.parent = dn.name
                        where dni.item_code = %s
                        and dn.patient = %s
                        and dn.docstatus = 1
                        order by posting_date desc
                        limit 1"""
            % ("%s", "%s"),
            (item.item_code, doc.patient),
            as_dict=1,
        )
        if len(items_list):
            item.last_qty_prescribed = items_list[0].get("stock_qty")
            item.last_date_prescribed = items_list[0].get("posting_date")


def set_missing_values(doc):
    if doc.reference_doctype and doc.reference_name:
        if doc.reference_doctype == "Patient Encounter":
            doc.patient = frappe.get_value(
                "Patient Encounter", doc.reference_name, "patient"
            )


def before_submit(doc, method):
    for item in doc.items:
        if item.is_restricted and not item.approval_number:
            frappe.throw(
                _(
                    "Approval number required for {0}. Please open line {1} and set the Approval Number."
                ).format(item.item_name, item.idx)
            )

def on_submit(doc, method):
    update_drug_prescription(doc)

def update_drug_prescription(doc):
    if doc.patient and not doc.is_return:
        if doc.form_sales_invoice:
            sales_invoice_doc = frappe.get_doc("Sales Invoice", doc.form_sales_invoice)

            for item in sales_invoice_doc.items:
                if item.reference_dt == "Drug Prescription":
                    for dni in doc.items:
                        if (
                            item.name == dni.si_detail and 
                            item.item_code == dni.item_code and 
                            item.parent == dni.against_sales_invoice
                        ):
                            if item.qty != dni.stock_qty:
                                quantity = dni.stock_qty
                            else:
                                quantity = item.quantity

                            frappe.db.set_value("Drug Prescription", item.reference_dn, {
                                "dn_detail": dni.name,
                                "quantity": quantity,
                                "delivered_quantity": quantity - item.quantity_returned
                            })
        
        else:
            if doc.reference_doctype == "Patient Encounter":
                patient_encounter_doc = frappe.get_doc(doc.reference_doctype, doc.reference_name)

                for dni in doc.items:
                    if dni.reference_doctype == "Drug Prescription":
                        for item in patient_encounter_doc.drug_prescription:
                            if (
                                dni.item_code == item.drug_code and 
                                dni.reference_name == item.name and 
                                dni.reference_doctype == item.doctype
                            ):
                                item.dn_detail = dni.name
                                if item.quantity != dni.stock_qty:
                                    item.quantity = dni.stock_qty
                                item.delivered_quantity = item.quantity - item.quantity_returned
                                item.db_update()

# frappe.db.sql("""
#     UPDATE `tabDrug Prescription` dp
#     INNER JOIN `tabDelivery Note Item` dni ON dp.name = dni.reference_name
#     SET dp.quantity = dni.stock_qty, dp.dn_detail = dni.name
#     WHERE dni.stock_qty != dp.quantity
#         AND dni.reference_doctype = "Drug Prescription"
#         AND dni.parent = '{0}'""".format(doc.name))
