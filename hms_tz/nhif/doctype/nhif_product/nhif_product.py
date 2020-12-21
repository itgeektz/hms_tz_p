# -*- coding: utf-8 -*-
# Copyright (c) 2020, Aakvatech and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document

class NHIFProduct(Document):
	pass


def add_product(id, name=None):
	if frappe.db.exists('NHIF Product', id):
		if name and name != "null":
			doc = frappe.get_doc('NHIF Product', id)
			if not doc.product_name:
				doc.product_name = name
				doc.save(ignore_permissions=True)
				frappe.db.commit()
	else:
		doc = frappe.new_doc('NHIF Product')
		doc.product_id = id
		if name and name != "null":
			doc.product_name = name
		doc.save(ignore_permissions=True)
		frappe.db.commit()
	return id