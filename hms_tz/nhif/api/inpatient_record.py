# -*- coding: utf-8 -*-
# Copyright (c) 2021, Aakvatech and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe import _
from frappe.utils import nowdate, nowtime, get_url_to_form
from hms_tz.nhif.api.healthcare_utils import get_item_rate, get_item_price
from hms_tz.nhif.api.patient_appointment import get_mop_amount
from hms_tz.nhif.api.patient_encounter import create_healthcare_docs_from_name
from hms_tz.nhif.api.patient_appointment import get_discount_percent
from erpnext.accounts.party import get_party_account
from erpnext.accounts.doctype.sales_invoice.sales_invoice import get_bank_cash_account
from hms_tz.nhif.api.healthcare_utils import (
    get_healthcare_service_order_to_invoice,
    get_warehouse_from_service_unit,
)
import json


def validate(doc, method):
    set_beds_price(doc)
    validate_inpatient_occupancies(doc)


def validate_inpatient_occupancies(doc):
    if doc.is_new():
        return
    old_doc = frappe.get_doc(doc.doctype, doc.name)
    count = 0
    for old_row in old_doc.inpatient_occupancies:
        count += 1
        if not old_row.is_confirmed:
            continue
        valid = True
        row = doc.inpatient_occupancies[count - 1]
        if str(row.check_in) != str(old_row.check_in):
            valid = False
        if str(row.check_out) != str(old_row.check_out):
            valid = False
        if str(row.amount) != str(old_row.amount):
            valid = False
        if row.left != old_row.left:
            valid = False
        if row.service_unit != old_row.service_unit:
            valid = False
        if not valid:
            frappe.msgprint(
                _(
                    "In Inpatient Occupancy line '{0}' has been invoiced. It should not be modified or deleted"
                ).format(old_row.idx)
            )


def daily_update_inpatient_occupancies():
    occupancies = frappe.get_all("Inpatient Record", filters={"status": "Admitted"})

    for item in occupancies:
        try:
            doc = frappe.get_doc("Inpatient Record", item.name)
            occupancies_len = len(doc.inpatient_occupancies)
            if occupancies_len > 0:
                last_row = doc.inpatient_occupancies[occupancies_len - 1]
                if not last_row.left:
                    last_row.left = 1
                    last_row.check_out = nowdate()
                    new_row = doc.append("inpatient_occupancies", {})
                    new_row.check_in = nowdate()
                    new_row.left = 0
                    new_row.service_unit = last_row.service_unit
                    doc.save(ignore_permissions=True)
                    frappe.db.commit()
        except Exception:
            frappe.log_error(frappe.get_traceback(), str("Daily Update Beds"))
            continue


@frappe.whitelist()
def confirmed(row, doc):
    row = frappe._dict(json.loads(row))
    doc = frappe._dict(json.loads(doc))
    if row.invoiced or not row.left:
        return
    encounter = frappe.get_doc("Patient Encounter", doc.admission_encounter)
    service_unit_type, warehouse = frappe.get_cached_value(
        "Healthcare Service Unit", row.service_unit, ["service_unit_type", "warehouse"]
    )
    item_code = frappe.get_cached_value(
        "Healthcare Service Unit Type", service_unit_type, "item_code"
    )
    item_rate = 0
    if encounter.insurance_subscription:
        item_rate = get_item_rate(
            item_code,
            encounter.company,
            encounter.insurance_subscription,
            encounter.insurance_company,
        )
        if not item_rate:
            frappe.throw(
                _(
                    "There is no price in Insurance Subscription {0} for item {1}"
                ).format(encounter.insurance_subscription, item_code)
            )
    elif encounter.mode_of_payment:
        price_list = frappe.get_cached_value(
            "Mode of Payment", encounter.mode_of_payment, "price_list"
        )
        if not price_list:
            frappe.throw(
                _("There is no in mode of payment {0}").format(
                    encounter.mode_of_payment
                )
            )
        if price_list:
            item_rate = get_item_price(item_code, price_list, encounter.company)
            if not item_rate:
                frappe.throw(
                    _("There is no price in price list {0} for item {1}").format(
                        price_list, item_code
                    )
                )

    if item_rate:
        delivery_note = create_delivery_note(
            encounter, item_code, item_rate, warehouse, row, doc.primary_practitioner
        )
        frappe.set_value(row.doctype, row.name, "is_confirmed", 1)
        return delivery_note


def create_delivery_note(encounter, item_code, item_rate, warehouse, row, practitioner):
    insurance_subscription = encounter.insurance_subscription
    insurance_company = encounter.insurance_company
    if not insurance_subscription:
        return

    # apply discount if it is available on Heathcare Insurance Company
    discount_percent = 0
    if insurance_company and "NHIF" not in insurance_company:
        discount_percent = get_discount_percent(insurance_company)

    items = []
    item = frappe.new_doc("Delivery Note Item")
    item.item_code = item_code
    # item.item_name = item_name
    item.warehouse = warehouse
    item.qty = 1
    item.rate = item_rate - (item_rate * (discount_percent / 100))
    item.reference_doctype = row.doctype
    item.reference_name = row.name
    item.description = "For Inpatient Record {0}".format(row.parent)
    items.append(item)

    doc = frappe.get_doc(
        dict(
            doctype="Delivery Note",
            posting_date=nowdate(),
            posting_time=nowtime(),
            set_warehouse=warehouse,
            company=encounter.company,
            customer=frappe.get_cached_value(
                "Healthcare Insurance Company", insurance_company, "customer"
            ),
            currency=frappe.get_cached_value(
                "Company", encounter.company, "default_currency"
            ),
            items=items,
            reference_doctype=row.parenttype,
            reference_name=row.parent,
            patient=encounter.patient,
            patient_name=encounter.patient_name,
            healthcare_service_unit=row.service_unit,
            healthcare_practitioner=practitioner,
        )
    )
    doc.flags.ignore_permissions = True
    doc.set_missing_values()
    doc.insert(ignore_permissions=True)
    doc.submit()
    if doc.get("name"):
        frappe.msgprint(
            _("Delivery Note {0} created successfully.").format(frappe.bold(doc.name))
        )
        return doc.get("name")


def set_beds_price(self):
    if not self.inpatient_occupancies:
        return

    # apply discount if it is available on Heathcare Insurance Company
    discount_percent = 0
    if self.insurance_company and "NHIF" not in self.insurance_company:
        discount_percent = get_discount_percent(self.insurance_company)

    for bed in self.inpatient_occupancies:
        if bed.amount == 0:
            if self.insurance_subscription:
                service_unit_type = frappe.get_cached_value(
                    "Healthcare Service Unit", bed.service_unit, "service_unit_type"
                )
                item_code = frappe.get_cached_value(
                    "Healthcare Service Unit Type", service_unit_type, "item_code"
                )
                item_price = get_item_rate(
                    item_code, self.company, self.insurance_subscription
                )
                bed.amount = item_price - (item_price * (discount_percent / 100))
                if discount_percent > 0:
                    bed.hms_tz_is_discount_applied = 1
                payment_type = "Insurance"
            else:
                mode_of_payment = frappe.get_value(
                    "Patient Encounter", self.admission_encounter, "mode_of_payment"
                )
                service_unit_type = frappe.get_cached_value(
                    "Healthcare Service Unit", bed.service_unit, "service_unit_type"
                )
                item_code = frappe.get_cached_value(
                    "Healthcare Service Unit Type", service_unit_type, "item_code"
                )
                bed.amount = get_mop_amount(
                    item_code, mode_of_payment, self.company, self.patient
                )
                payment_type = mode_of_payment
            frappe.msgprint(
                _("{3} Bed prices set for {0} as of {1} for amount {2}").format(
                    item_code, str(bed.check_in), str(bed.amount), payment_type
                )
            )


def after_insert(doc, method):
    create_healthcare_docs_from_name(doc.admission_encounter)


@frappe.whitelist()
def make_deposit(inpatient_record, deposit_amount, mode_of_payment):
    if float(deposit_amount) <= 0:
        frappe.throw(_("<b>Deposit amount cannot be less than or equal to zero</b>"))

    if not mode_of_payment:
        frappe.throw(_("The mode of payment is required"))

    inpatient_record_doc = frappe.get_doc("Inpatient Record", inpatient_record)
    if inpatient_record_doc.insurance_subscription:
        frappe.throw(_("You cannot make deposit for insurance patient"))

    customer = frappe.get_cached_value(
        "Patient", inpatient_record_doc.patient, "customer"
    )

    try:
        payment = frappe.new_doc("Payment Entry")
        payment.posting_date = nowdate()
        payment.payment_type = "Receive"
        payment.party_type = "Customer"
        payment.party = customer
        payment.company = inpatient_record_doc.company
        payment.mode_of_payment = str(mode_of_payment)
        payment.paid_from = get_party_account(
            "Customer", customer, inpatient_record_doc.company
        )
        payment.paid_to = get_bank_cash_account(
            mode_of_payment, inpatient_record_doc.company
        )["account"]
        payment.paid_amount = float(deposit_amount)
        payment.received_amount = float(deposit_amount)
        payment.source_exchange_rate = 1
        payment.target_exchange_rate = 1
        payment.setup_party_account_field()
        payment.set_missing_values()
        payment.save()
        payment.reload()
        payment.submit()
        url = get_url_to_form(payment.doctype, payment.name)
        frappe.msgprint(
            "Payment Entry: <a href='{0}'>{1}</a> for Deposit is created successful".format(
                url, frappe.bold(payment.name)
            )
        )
        return payment.name
    except Exception as e:
        frappe.msgprint(_(f"Error: <b>{e}</b>"))
        return False


@frappe.whitelist()
def create_sales_invoice(args):
    args = frappe._dict(json.loads(args))
    patient_encounter_list = frappe.get_all(
        "Patient Encounter",
        filters={
            "docstatus": 1,
            "patient": args.patient,
            "appointment": args.appointment_no,
            "inpatient_record": args.inpatient_record,
        },
        fields=["name", "inpatient_record"],
    )
    if len(patient_encounter_list) == 0:
        frappe.msgprint(
            _(
                "No Patient Encounters found for this Inpatient Record: <b>{inpatient_record}</b> and Patient Appointment: <b>{appointment_no}</b>"
            )
        )
        return False

    services = get_healthcare_service_order_to_invoice(
        patient=args.patient,
        company=args.company,
        patient_encounter_list=patient_encounter_list,
    )
    if len(services) == 0:
        frappe.msgprint(
            _(
                "No Healthcare Services found for this Inpatient Record: <b>{inpatient_record}</b> and Patient Appointment: <b>{appointment_no}</b>"
            )
        )
        return False

    invoice_doc = frappe.new_doc("Sales Invoice")
    invoice_doc.patient = args.patient
    invoice_doc.customer = frappe.get_cached_value("Patient", args.patient, "customer")
    invoice_doc.company = args.company
    mode_of_payment = frappe.get_value(
        "Patient Encounter", patient_encounter_list[0].name, "mode_of_payment"
    )
    price_list = frappe.get_cached_value(
        "Mode of Payment", mode_of_payment, "price_list"
    )

    for service in services:
        item = invoice_doc.append("items", {})
        item.item_code = service.get("service")
        item.qty = service.get("qty")
        item.rate = get_item_price(service.get("service"), price_list, args.company)
        item.amount = item.rate * item.qty
        item.reference_dt = service.get("reference_type")
        item.reference_dn = service.get("reference_name")
        if item.reference_dt == "Drug Prescription":
            item.healthcare_service_unit = frappe.get_value(
                service.get("reference_type"),
                service.get("reference_name"),
                "healthcare_service_unit",
            )
            item.warehouse = get_warehouse_from_service_unit(
                item.healthcare_service_unit
            )

    invoice_doc.is_pos = 0
    invoice_doc.allocate_advances_automatically = 1
    invoice_doc.set_missing_values()
    invoice_doc.set_taxes()
    invoice_doc.save()

    return invoice_doc.name
