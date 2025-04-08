# -*- coding: utf-8 -*-
# Copyright (c) 2018, ESS LLP and contributors
# For license information, please see license.txt


import json

import frappe
from frappe.utils import cint
import re

@frappe.whitelist()
def get_feed(name, document_types=None, date_range=None,practitioner = None, start=0, page_length=20):
	filters, or_filters = get_filters(name, document_types, date_range, practitioner)
	#frappe.msgprint(f"filters:  {filters.get('filters_or')}")
	data = frappe.db.get_all(
		"Patient Medical Record",
		fields=["name", "owner", "communication_date", "reference_doctype", "reference_name", "subject","reference_owner"],
		filters=filters,
        or_filters=or_filters,
		order_by="communication_date DESC",
		limit=cint(page_length),
		start=cint(start),
	)
	result = []
	if data:
		for data in data:
			if frappe.get_value(data.reference_doctype,data.reference_name,'docstatus') == 1:
				result.append(data)
	return result

def get_filters(name, document_types=None, date_range=None, practitioner=None):
    filters = {"patient": name}
    or_filters = []

    
    if document_types:
        document_types = json.loads(document_types)
        if len(document_types):
            filters["reference_doctype"] = ["in", document_types]

    if date_range:
        try:
            date_range = json.loads(date_range)
            
            if date_range:
                filters["communication_date"] = ["between", [date_range[0], date_range[1]]]
        except json.decoder.JSONDecodeError:
            pass

    # Add OR filter for practitioner based on name found in `subject` HTML
    if practitioner:
        try:
            practitioner_list = json.loads(practitioner)
            if practitioner_list:
                subject_conditions = []
                for name in practitioner_list:
                    or_filters.append(["subject", "like", f"%{name}%"])

                
        except (json.JSONDecodeError, TypeError):
            pass

    return filters, or_filters


@frappe.whitelist()
def get_feed_for_dt(doctype, docname,practitioner):
	"""get feed"""
	result = frappe.db.get_all(
		"Patient Medical Record",
		fields=["name", "owner", "communication_date", "reference_doctype", "reference_name", "subject","practitioner"],
		filters={"reference_doctype": doctype, "reference_name": docname,"practitioner":practitioner},
		order_by="communication_date DESC",
	)

	return result


@frappe.whitelist()
def get_patient_history_doctypes():
	document_types = []
	settings = frappe.get_single("Patient History Settings")

	for entry in settings.standard_doctypes:
		document_types.append(entry.document_type)

	for entry in settings.custom_doctypes:
		document_types.append(entry.document_type)

	return document_types
@frappe.whitelist()
def get_practitioner():
	practitioner = []
	
	practitioner = frappe.db.get_list("Healthcare Practitioner", pluck="name")
	
	return practitioner

@frappe.whitelist()
def reset_filters():
	"""reset filters"""
	frappe.local.form_dict.document_types = None
	frappe.local.form_dict.date_range = None
	frappe.local.form_dict.practitioner = None

	return {
		"document_types": None,
		"date_range": None,
		"practitioner": None
	}