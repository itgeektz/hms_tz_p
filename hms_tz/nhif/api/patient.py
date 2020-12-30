# -*- coding: utf-8 -*-
# Copyright (c) 2020, Aakvatech and contributors
# For license information, please see license.txt

from __future__ import unicode_literals 
import frappe
from frappe import _
from hms_tz.nhif.api.token import get_nhifservice_token
from erpnext import get_company_currency, get_default_company
import json
import requests
from time import sleep
from hms_tz.nhif.doctype.nhif_product.nhif_product import add_product
from hms_tz.nhif.doctype.nhif_scheme.nhif_scheme import add_scheme
from frappe.utils import nowdate, getdate
from hms_tz.nhif.doctype.nhif_response_log.nhif_response_log import add_log
from hms_tz.nhif.api.healthcare_utils import remove_special_characters
from datetime import date


def validate(doc, method):
    # validate date of birth
    if date.today() < getdate(doc.dob):
        frappe.throw(_("The date of birth cannot be later than today's date"))
    # replace initial 0 with 255 and remove all the unnecessray characters
    doc.mobile = remove_special_characters(doc.mobile)
    if doc.mobile[0] == "0":
        doc.mobile = "255" + doc.mobile[1:]
    if doc.next_to_kin_mobile_no:
        doc.next_to_kin_mobile_no = remove_special_characters(doc.next_to_kin_mobile_no)
        if doc.next_to_kin_mobile_no[0] == "0":
            doc.next_to_kin_mobile_no = "255" + doc.next_to_kin_mobile_no[1:]
    validate_mobile_number(doc.name, doc.mobile)

@frappe.whitelist()
def validate_mobile_number(doc_name, mobile=None):
    if mobile:
        mobile_patients_list = frappe.get_all("Patient", 
            filters = {
                "mobile" : mobile,
                "name" : ['!=', doc_name]
            }
        )
        if len(mobile_patients_list) > 0:
            frappe.msgprint(_("This mobile number is used by another patient"))


@frappe.whitelist()
def get_patient_info(card_no = None):
    if not card_no:
        frappe.msgprint(_("Please set Card No"))
        return
    company = get_default_company() ## TODO: need to be fixed to support pultiple company
    token = get_nhifservice_token(company)
    
    nhifservice_url = frappe.get_value("Company NHIF Settings", company, "nhifservice_url")
    headers = {
        "Authorization" : "Bearer " + token
    }
    url = str(nhifservice_url) + "/nhifservice/breeze/verification/GetCardDetails?CardNo=" + str(card_no)
    for i in range(3):
        try:
            r = requests.get(url, headers = headers, timeout=5)
            r.raise_for_status()
            frappe.logger().debug({"webhook_success": r.text})
            if json.loads(r.text):
                add_log(
					request_type = "GetCardDetails", 
					request_url = url, 
					request_header = headers, 
					response_data = json.loads(r.text) 
				)
                card = json.loads(r.text)
                frappe.msgprint(_(card["Remarks"]), alert=True)
                add_scheme(card.get("SchemeID"), card.get("SchemeName"))
                add_product(card.get("ProductCode"), card.get("ProductName"))
                return card
            else:
                add_log(
					request_type = "GetCardDetails", 
					request_url = url, 
					request_header = headers, 
				)
                frappe.throw(json.loads(r.text))
        except Exception as e:
            frappe.logger().debug({"webhook_error": e, "try": i + 1})
            sleep(3 * i + 1)
            if i != 2:
                continue
            else:
                raise e
