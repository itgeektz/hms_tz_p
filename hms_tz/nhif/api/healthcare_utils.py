# -*- coding: utf-8 -*-
# Copyright (c) 2018, earthians and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe import _
from erpnext.healthcare.doctype.healthcare_settings.healthcare_settings import get_income_account
from hms_tz.hms_tz.utils import validate_customer_created
from hms_tz.nhif.api.patient_appointment import get_insurance_amount
from frappe.utils import nowdate, nowtime
import base64
import re


@frappe.whitelist()
def get_healthcare_services_to_invoice(patient, company, encounter=None, service_order_category=None, prescribed=None):
    patient = frappe.get_doc('Patient', patient)
    items_to_invoice = []
    if patient:
        validate_customer_created(patient)
        # Customer validated, build a list of billable services
        if encounter:
            items_to_invoice += get_healthcare_service_order_to_invoice(
                patient, company, encounter, service_order_category, prescribed)
        return items_to_invoice


def get_healthcare_service_order_to_invoice(patient, company, encounter, service_order_category=None, prescribed=None):
    encounter_dict = frappe.get_all("Patient Encounter", filters={
        "reference_encounter": encounter,
        "docstatus": 1,
    })
    encounter_list = [encounter]

    for i in encounter_dict:
        encounter_list.append(i.name)

    filters = {
        'patient': patient.name,
        'company': company,
        'order_group': ["in", encounter_list],
        'invoiced': False,
        'docstatus': 1
    }

    if service_order_category:
        filters['healthcare_service_order_category'] = service_order_category
    if prescribed:
        filters['prescribed'] = prescribed
    services_to_invoice = []
    services = frappe.get_list(
        'Healthcare Service Order',
        fields=['*'],
        filters=filters
    )

    if services:
        for service in services:
            practitioner_charge = 0
            income_account = None
            service_item = None
            if service.order_doctype and service.order:
                is_not_available_inhouse = frappe.get_value(
                    service.order_doctype, service.order, "is_not_available_inhouse")
                if not is_not_available_inhouse:
                    continue
            if service.ordered_by:
                service_item = service.billing_item
                practitioner_charge = get_insurance_amount(
                    service.insurance_subscription, service.billing_item, company, patient.name, service.insurance_company)
                income_account = get_income_account(
                    service.ordered_by, company)

            services_to_invoice.append({
                'reference_type': 'Healthcare Service Order',
                'reference_name': service.name,
                'service': service_item,
                'rate': practitioner_charge,
                'income_account': income_account
            })

    return services_to_invoice


def get_item_price(item_code, price_list, company):
    price = 0
    company_currency = frappe.get_value("Company", company, "default_currency")
    item_prices_data = frappe.get_all("Item Price",
                                      fields=[
                                          "item_code", "price_list_rate", "currency"],
                                      filters={
                                          'price_list': price_list, 'item_code': item_code, 'currency': company_currency},
                                      order_by="valid_from desc"
                                      )
    if len(item_prices_data):
        price = item_prices_data[0].price_list_rate
    return price


def get_item_rate(item_code, company, insurance_subscription, insurance_company):
    price_list = None
    price_list_rate = None
    if insurance_subscription:
        hic_plan = frappe.get_value(
            "Healthcare Insurance Subscription", insurance_subscription, "healthcare_insurance_coverage_plan")
        price_list = frappe.get_value(
            "Healthcare Insurance Coverage Plan", hic_plan, "price_list")
        if price_list:
            price_list_rate = get_item_price(item_code, price_list, company)
            if price_list_rate and price_list_rate != 0:
                return price_list_rate
            else:
                price_list_rate = None

    if not price_list_rate and insurance_company:
        price_list = frappe.get_value(
            "Healthcare Insurance Company", insurance_company, "default_price_list")
    if not price_list:
        frappe.throw(
            _("Please set Price List in Healthcare Insurance Coverage Plan"))
    else:
        price_list_rate = get_item_price(item_code, price_list, company)
    if price_list_rate == (0 or None):
        frappe.throw(
            _("Please set Price List for item: {0}").format(item_code))
    return price_list_rate


def to_base64(value):
    data = base64.b64encode(value)
    return str(data)[2:-1]


def remove_special_characters(text):
    return re.sub('[^A-Za-z0-9]+', '', text)


def get_app_branch(app):
    '''Returns branch of an app'''
    import subprocess
    try:
        branch = subprocess.check_output('cd ../apps/{0} && git rev-parse --abbrev-ref HEAD'.format(app),
                                         shell=True)
        branch = branch.decode('utf-8')
        branch = branch.strip()
        return branch
    except Exception:
        return ''


def create_delivery_note_from_LRPT(LRPT_doc, patient_encounter_doc):
    if not patient_encounter_doc.appointment:
        return
    insurance_subscription, insurance_company = frappe.get_value(
        "Patient Appointment", patient_encounter_doc.appointment, ["insurance_subscription", "insurance_company"])
    if not insurance_subscription:
        return
    warehouse = get_warehouse_from_service_unit(
        patient_encounter_doc.healthcare_service_unit)
    items = []
    item = get_item_form_LRPT(LRPT_doc)
    item_code = item.get("item_code")
    if not item_code:
        return
    is_stock, item_name = frappe.get_value(
        "Item", item_code, ["is_stock_item", "item_name"])
    if is_stock:
        return
    item_row = frappe.new_doc("Delivery Note Item")
    item_row.item_code = item_code
    item_row.item_name = item_name
    item_row.warehouse = warehouse
    item_row.qty = item.qty
    item_row.rate = get_item_rate(
        item_code, patient_encounter_doc.company, insurance_subscription, insurance_company)
    item_row.reference_doctype = LRPT_doc.doctype
    item_row.reference_name = LRPT_doc.name
    item_row.description = frappe.get_value("Item", item_code, "description")
    items.append(item_row)

    if len(items) == 0:
        return
    doc = frappe.get_doc(dict(
        doctype="Delivery Note",
        posting_date=nowdate(),
        posting_time=nowtime(),
        set_warehouse=warehouse,
        company=patient_encounter_doc.company,
        customer=frappe.get_value(
            "Healthcare Insurance Company", insurance_company, "customer"),
        currency=frappe.get_value(
            "Company", patient_encounter_doc.company, "default_currency"),
        items=items,
        reference_doctype=LRPT_doc.doctype,
        reference_name=LRPT_doc.name,
        patient=patient_encounter_doc.patient,
        patient_name=patient_encounter_doc.patient_name
    ))
    doc.set_missing_values()
    doc.flags.ignore_permissions = True
    doc.insert()
    doc.submit()
    if doc.get('name'):
        frappe.msgprint(_('Delivery Note {0} created successfully.').format(
            frappe.bold(doc.name)), alert=True)


def get_warehouse_from_service_unit(healthcare_service_unit):
    warehouse = frappe.get_value(
        "Healthcare Service Unit", healthcare_service_unit, "warehouse")
    if not warehouse:
        frappe.throw(_("Warehouse is missing in Healthcare Service Unit"))
    return warehouse


def get_item_form_LRPT(LRPT_doc):
    item = frappe._dict()
    if LRPT_doc.doctype == "Lab Test":
        item.item_code = frappe.get_value(
            "Lab Test Template", LRPT_doc.template, "item")
        item.qty = 1
    elif LRPT_doc.doctype == "Radiology Examination":
        item.item_code = frappe.get_value(
            "Radiology Examination Template", LRPT_doc.radiology_examination_template, "item")
        item.qty = 1
    elif LRPT_doc.doctype == "Clinical Procedure":
        item.item_code = frappe.get_value(
            "Clinical Procedure Template", LRPT_doc.procedure_template, "item")
        item.qty = 1
    elif LRPT_doc.doctype == "Therapy Plan":
        item.item_code = None
        item.qty = 0
    return item
