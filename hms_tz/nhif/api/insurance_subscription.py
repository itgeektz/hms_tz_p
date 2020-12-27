# -*- coding: utf-8 -*-
# Copyright (c) 2020, Aakvatech and contributors
# For license information, please see license.txt

from __future__ import unicode_literals 
import frappe
# from frappe import _


def on_submit(doc, method):
    set_insurance_card_detail_in_patient(doc)


def on_cancel(doc, method):
    set_insurance_card_detail_in_patient(doc)


def set_insurance_card_detail_in_patient(doc):
    his_list = frappe.get_all("Healthcare Insurance Subscription",
        filtes = {
          "patient" : doc.patient,
          "docstatus": 1,
        },
        fields = ["coverage_plan_card_number"]
    )
    str_coverage_plan_card_number = ""
    for card in his_list:
        if card.coverage_plan_card_number:
            str_coverage_plan_card_number += card.coverage_plan_card_number + ", "
    
    frappe.set_value("Patient", doc.patient, "insurance_card_detail", str_coverage_plan_card_number)