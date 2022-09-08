from __future__ import unicode_literals
import frappe
from frappe import _
import json
from hms_tz.nhif.api.healthcare_utils import update_dimensions


def validate(doc, method):
    if doc.docstatus != 0:
        return
    set_prescribed(doc)
    set_missing_values(doc)
    check_item_for_out_of_stock(doc)
    update_dimensions(doc)


def after_insert(doc, method):
    set_original_item(doc)


def set_original_item(doc):
    for item in doc.items:
        if item.item_code:
            item.original_item = item.item_code
            item.original_stock_uom_qty = item.stock_qty

        new_row = item.as_dict()
        for fieldname in get_fields_to_clear():
            new_row[fieldname] = None

        new_row.update(
            {
                "parent": doc.name,
                "parentfield": "hms_tz_original_items",
                "parenttype": "Delivery Note",
                "doctype": "Original Delivery Note Item",
            }
        )
        doc.append("hms_tz_original_items", new_row)
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
    if (
        not doc.patient
        and doc.reference_doctype
        and doc.reference_name
        and doc.reference_doctype == "Patient Encounter"
    ):
        doc.patient = frappe.get_value(
            "Patient Encounter", doc.reference_name, "patient"
        )

    if not doc.hms_tz_phone_no:
        doc.hms_tz_phone_no = frappe.get_value("Patient", doc.patient, "mobile")

    if doc.form_sales_invoice:
        if not doc.hms_tz_appointment_no or not doc.healthcare_practitioner:
            si_reference_dn = frappe.get_value(
                "Sales Invoice Item", doc.items[0].si_detail, "reference_dn"
            )

            if si_reference_dn:
                parent_encounter = frappe.get_value(
                    "Drug Prescription", si_reference_dn, "parent"
                )
                (
                    doc.hms_tz_appointment_no,
                    doc.healthcare_practitioner,
                ) = frappe.get_value(
                    "Patient Encounter",
                    parent_encounter,
                    ["appointment", "practitioner"],
                )


def before_submit(doc, method):
    if doc.hms_tz_all_items_out_of_stock == 1:
        frappe.throw(
            "<h4 class='font-weight-bold bg-warning text-center'>\
            This Delivery Note can't be submitted because all Items\
                are not available in stock</h4>"
        )

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
                            item.name == dni.si_detail
                            and item.item_code == dni.item_code
                            and item.parent == dni.against_sales_invoice
                        ):
                            if item.qty != dni.stock_qty:
                                quantity = dni.stock_qty
                            else:
                                quantity = item.qty

                            frappe.db.set_value(
                                "Drug Prescription",
                                item.reference_dn,
                                {
                                    "dn_detail": dni.name,
                                    "quantity": quantity,
                                    "delivered_quantity": quantity,
                                },
                            )

                    for original_item in doc.hms_tz_original_items:
                        if (
                            original_item.hms_tz_is_out_of_stock == 1
                            and item.name == original_item.si_detail
                            and item.item_code == original_item.item_code
                            and item.parent == original_item.against_sales_invoice
                        ):
                            frappe.db.set_value(
                                "Drug Prescription",
                                item.reference_dn,
                                {
                                    "is_not_available_inhouse": 1,
                                    "hms_tz_is_out_of_stcok": 1,
                                    "is_cancelled": 1,
                                },
                            )

        else:
            if doc.reference_doctype == "Patient Encounter":
                patient_encounter_doc = frappe.get_doc(
                    doc.reference_doctype, doc.reference_name
                )

                for dni in doc.items:
                    if dni.reference_doctype == "Drug Prescription":
                        for item in patient_encounter_doc.drug_prescription:
                            if (
                                # commented to avoid mismatch of drug code of drug prescription and
                                # item code of delivery note item
                                # 2022-06-13
                                # dni.item_code == item.drug_code and
                                dni.reference_name == item.name
                                and dni.reference_doctype == item.doctype
                            ):
                                item.dn_detail = dni.name
                                if item.quantity != dni.stock_qty:
                                    item.quantity = dni.stock_qty
                                item.delivered_quantity = (
                                    item.quantity - item.quantity_returned
                                )
                                item.db_update()

                for original_item in doc.hms_tz_original_items:
                    if (
                        original_item.hms_tz_is_out_of_stock == 1
                        and original_item.reference_name
                        and original_item.reference_doctype == "Drug Prescription"
                    ):
                        for drug_item in patient_encounter_doc.drug_prescription:
                            if (
                                original_item.reference_name == drug_item.name
                                and original_item.reference_doctype == drug_item.doctype
                            ):
                                drug_item.is_not_available_inhouse = 1
                                drug_item.hms_tz_is_out_of_stock = 1
                                drug_item.is_cancelled = 1
                                drug_item.db_update()
                patient_encounter_doc.save(ignore_permissions=True)


def check_item_for_out_of_stock(doc):
    """Mark an Item as out of stock if it is not available in stock"""

    if len(doc.items) > 0 and len(doc.hms_tz_original_items) > 0:
        items = []

        doc.total = 0
        doc.total_qty = 0
        for dni_row in doc.items:
            for original_item in doc.hms_tz_original_items:
                if (
                    dni_row.hms_tz_is_out_of_stock == 1
                    and dni_row.item_code == original_item.item_code
                    and original_item.hms_tz_is_out_of_stock == 0
                ):
                    original_item.hms_tz_is_out_of_stock = 1

                if (
                    dni_row.hms_tz_is_out_of_stock == 0
                    and dni_row.item_code == original_item.item_code
                    and original_item.hms_tz_is_out_of_stock == 1
                ):
                    original_item.hms_tz_is_out_of_stock = 0

            if not dni_row.hms_tz_is_out_of_stock:
                dni_row.name = None
                items.append(dni_row)

                doc.total += dni_row.amount
                doc.total_qty += dni_row.qty

        doc.items = items
        if len(doc.items) > 0:
            doc.hms_tz_all_items_out_of_stock = 0
        else:
            check_out_of_stock_for_original_item(doc)


def check_out_of_stock_for_original_item(doc):
    """Copy items back to delivery note item table
    if all items marked as out of stock
    """
    doc.total = 0
    doc.total_qty = 0
    for original_item in doc.hms_tz_original_items:
        if original_item.hms_tz_is_out_of_stock == 1:
            new_item = original_item.as_dict()

            for fieldname in get_fields_to_clear():
                new_item[fieldname] = None

            new_item.update(
                {
                    "hms_tz_is_out_of_stock": 1,
                    "parent": doc.name,
                    "parentfield": "items",
                    "parenttype": "Delivery Note",
                    "doctype": "Delivery Note Item",
                }
            )
            doc.append("items", frappe.get_doc(new_item).as_dict())

            original_item.hms_tz_is_out_of_stock = 1

            doc.total += new_item.amount
            doc.total_qty += new_item.qty

    doc.hms_tz_all_items_out_of_stock = 1
    frappe.msgprint(
        "<h4 class='font-weight-bold bg-warning text-center'>All Items are marked as Out of Stock</h4>"
    )


@frappe.whitelist()
def convert_to_instock_item(name, row):
    """Convert an item to be considered as it is available in stock

    :param name: Name of the current document.
    :param row: Original child row to be converted.
    """
    new_row = json.loads(row)

    for fieldname in get_fields_to_clear():
        new_row[fieldname] = None

    new_row.update(
        {
            "hms_tz_is_out_of_stock": 0,
            "parent": name,
            "parentfield": "items",
            "parenttype": "Delivery Note",
            "doctype": "Delivery Note Item",
        }
    )
    doc = frappe.get_doc("Delivery Note", name)
    prev_size = len(doc.items)
    doc.append("items", new_row)

    if len(doc.items) > prev_size:
        doc.total_qty += new_row.get("qty")
        doc.total += new_row.get("amount")

        for original_item in doc.hms_tz_original_items:
            if original_item.item_code == new_row.get("item_code"):
                original_item.hms_tz_is_out_of_stock = 0

        doc.save(ignore_permissions=True)
        doc.reload()
        return True


def get_fields_to_clear():
    return ["name", "owner", "creation", "modified", "modified_by", "docstatus"]
