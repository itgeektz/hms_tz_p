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
from frappe.utils import now
from hms_tz.nhif.doctype.nhif_response_log.nhif_response_log import add_log



def validate(doc, method):
    if  now() < doc.dob:
        frappe.throw(_("The date of birth cannot be later than today's date"))


@frappe.whitelist()
def get_patinet_info(card_no = None):
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

