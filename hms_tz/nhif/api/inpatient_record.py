# -*- coding: utf-8 -*-
# Copyright (c) 2021, Aakvatech and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe import _
from frappe.utils import nowdate


def daily_update_inpatient_occupancies():
    occupancies = frappe.get_all(
        "Inpatient Record", filters={"status": "Admitted"})

    for item in occupancies:
        doc = frappe.get_doc("Inpatient Record", item.name)
        occupancies_len = len(doc.inpatient_occupancies)
        if occupancies_len > 0:
            last_row = doc.inpatient_occupancies[occupancies_len-1]
            if not last_row.left:
                last_row.left = 1
                last_row.check_out = nowdate()
                new_row = doc.append('inpatient_occupancies', {})
                new_row.check_in = nowdate()
                new_row.left = 0
                new_row.service_unit = last_row.service_unit
                doc.save(ignore_permissions=True)
                frappe.db.commit()
