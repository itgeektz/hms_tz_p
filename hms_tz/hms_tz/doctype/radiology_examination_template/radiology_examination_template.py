    # -*- coding: utf-8 -*-
# Copyright (c) 2020, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document
from hms_tz.hms_tz.utils import create_item_from_doc, update_item_from_doc, on_trash_doc_having_item_reference
from hms_tz.nhif.api.healthcare_utils import validate_hsu_healthcare_template

class RadiologyExaminationTemplate(Document):
	def validate(self):
		update_item_from_doc(self, self.procedure_name)
		validate_hsu_healthcare_template(self)

	def after_insert(self):
		create_item_from_doc(self, self.procedure_name)

	def on_trash(self):
		on_trash_doc_having_item_reference(self)

