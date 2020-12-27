# -*- coding: utf-8 -*-
# Copyright (c) 2018, earthians and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import math
import frappe
from frappe import _
from hms_tz.hms_tz.doctype.healthcare_settings.healthcare_settings import get_income_account
from hms_tz.hms_tz.utils import validate_customer_created
from hms_tz.nhif.api.patient_appointment import get_insurance_amount
import base64


@frappe.whitelist()
def get_healthcare_services_to_invoice(patient, company, encounter=None, service_order_category=None, prescribed=None):
	patient = frappe.get_doc('Patient', patient)
	items_to_invoice = []
	if patient:
		validate_customer_created(patient)
		# Customer validated, build a list of billable services
		if encounter:
			items_to_invoice += get_healthcare_service_order_to_invoice(patient, company, encounter, service_order_category, prescribed)
		return items_to_invoice



def get_healthcare_service_order_to_invoice(patient, company, encounter, service_order_category=None, prescribed=None):
	encounter_dict = frappe.get_all("Patient Encounter",filters = {
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
			if service.ordered_by:
				service_item = service.billing_item
				practitioner_charge = get_insurance_amount(service.insurance_subscription, service.billing_item, company, patient.name, service.insurance_company)
				income_account = get_income_account(service.ordered_by, company)

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
    if  insurance_subscription:
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
            frappe.throw(_("Please set Price List in Healthcare Insurance Coverage Plan"))
    else:
        price_list_rate = get_item_price(item_code, price_list, company)
    if price_list_rate == (0 or None):
        frappe.throw(_("Please set Price List for item: {0}").format(item_code))
    return price_list_rate


def to_base64(value):
    data = base64.b64encode(value)
    return str(data)[2:-1]