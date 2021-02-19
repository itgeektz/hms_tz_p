# Copyright (c) 2013, Aakvatech and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe import _
from frappe.utils import nowdate
from hms_tz.nhif.api.token import get_claimsservice_token
from hms_tz.nhif.doctype.nhif_response_log.nhif_response_log import add_log
import json
import requests


def execute(filters=None):
    columns = get_columns()
    data = get_data(filters)
    return columns, data


def get_columns():
    columns = [
        {
            "fieldname": "SubmissionID",
            "label": _("Submission ID"),
            "fieldtype": "Data",
            "options": "",
            "width": 150
        },
        {
            "fieldname": "DateSubmitted",
            "label": _("Date Submitted"),
            "fieldtype": "Datetime",
            "options": "",
            "width": 150
        },
        {
            "fieldname": "ClaimYear",
            "label": _("Claim Year"),
            "fieldtype": "Data",
            "options": "",
            "width": 75
        },
        {
            "fieldname": "ClaimMonth",
            "label": _("Claim Month"),
            "fieldtype": "Data",
            "options": "",
            "width": 75
        },
        {
            "fieldname": "FolioNo",
            "label": _("Folio No"),
            "fieldtype": "Data",
            "options": "",
            "width": 100
        },
        {
            "fieldname": "BillNo",
            "label": _("Bill No"),
            "fieldtype": "Data",
            "options": "",
            "width": 100
        },
        {
            "fieldname": "SubmittedBy",
            "label": _("Submitted By"),
            "fieldtype": "Data",
            "options": "",
            "width": 100
        },
    ]
    return columns


def get_data(filters):
    data = get_nhif_data(filters)
    return data


def get_nhif_data(filters):
    token = get_claimsservice_token(filters.company)
    claimsserver_url, facility_code = frappe.get_value(
        "Company NHIF Settings", filters.company, ["claimsserver_url", "facility_code"])
    headers = {
        "Authorization": "Bearer " + token,
        "Content-Type": "application/json"
    }
    url = str(claimsserver_url) + \
        "/claimsserver/api/v1/Claims/getSubmittedClaims?FacilityCode={0}&ClaimYear={1}&ClaimMonth={2}".format(
            facility_code, filters.ClaimYear, filters.ClaimMonth)
    r = requests.get(url, headers=headers, timeout=300)
    if r.status_code != 200:
        add_log(
            request_type="getSubmittedClaims",
            request_url=url,
            request_header=headers,
            response_data=str(r.text) if r.text else str(r),
            status_code=r.status_code
        )
        frappe.throw(str(r.text) if r.text else str(r))
    else:
        if r.text:
            add_log(
                request_type="getSubmittedClaims",
                request_url=url,
                request_header=headers,
                response_data=r.text,
                status_code=r.status_code
            )
        if json.loads(r.text):
            frappe.msgprint(
                _("The claims has been load successfully"), alert=True)
            return json.loads(r.text)
