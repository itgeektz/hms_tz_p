# Copyright (c) 2023, Aakvatech and contributors
# For license information, please see license.txt

import frappe
from frappe.utils import nowdate, nowtime, get_fullname, get_url_to_form, flt
from frappe.model.document import Document

class PatientDiscountRequest(Document):
	def before_insert(self):
		self.set_missing_values()

	def after_insert(self):
		if self.sales_invoice:
			invoice_doc = frappe.get_doc("Sales Invoice", self.sales_invoice)
			invoice_doc.hms_tz_discount_requested = 1
			invoice_doc.hms_tz_discount_status = "Pending"
			invoice_doc.save(ignore_permissions=True)

			url = get_url_to_form("Patient Discount Request", self.name)
			invoice_doc.add_comment(
				comment_type="Comment",
				text=f"Patient Discount Request: <b>{invoice_doc.name}<b>\
					was successfully created. <br><br><br>\
					View it here: <a href='{url}'><b>{self.name}</b></a>"
			)
	
	def validate(self):
		self.validate_patient()
		self.get_insurance_details()
		self.set_discount_amount()
	
	def before_submit(self):
		self.approved_by = get_fullname(frappe.session.user)
	
	
	def set_missing_values(self):
		self.posting_date = nowdate()
		self.posting_time = nowtime()

		inpatient_record = frappe.get_value("Patient", self.patient, "inpatient_record")
		if inpatient_record:
			self.inpatient_record = inpatient_record
		
		self.requested_by = get_fullname(frappe.session.user)

	def validate_patient(self):
		if self.patient:
			if (
				self.sales_invoice and
				self.patient != frappe.db.get_value("Sales Invoice", self.sales_invoice, "patient")
			):
				frappe.throw(f"This sales invoice: {self.sales_invoice} is not for this patient: {self.patient}")
			
			if (
				self.inpatient_record and
				self.patient != frappe.db.get_value("Inpatient Record", self.inpatient_record, "patient")
			):
				frappe.throw(f"This inpatient record: {self.inpatient_record} is not for this patient: {self.patient}")

	def get_insurance_details(self):
		if self.appointment:
			(
				self.insurance_subscription,
				self.insurance_coverage_plan,
				self.insurance_company
			) = frappe.db.get_value(
				"Patient Appointment", self.appointment,
				["insurance_subscription", "coverage_plan_name", "insurance_company_name"]
			)
				
			if not self.insurance_subscription:
				frappe.throw(f"This appointment: {self.appointment} does not have an insurance subscription")

			if "NHIF" in self.insurance_company:
				frappe.throw(
					f"This appointment: <b>{self.appointment}</b> is for NHIF insurance. <br>Note:\
					<br>You can only request discount for Cash and Non NHIF Patients."
				)
	
	def set_discount_amount(self):
		if (
			self.apply_discount_on == "Grand Total"
			and self.sales_invoice
		):
			self.total_actual_amount = frappe.db.get_value("Sales Invoice", self.sales_invoice, "grand_total")
			discount_amount = 0
			if self.discount_percent:
				discount_amount = self.total_actual_amount * (self.discount_percent/100)
			elif self.discount_amount:
				discount_amount = self.discount_amount
			self.total_amount_after_discount = self.total_actual_amount - discount_amount
			self.total_discounted_amount = discount_amount

		elif (
			self.apply_discount_on == "Net Total"
			and self.sales_invoice
		):
			self.total_actual_amount = frappe.db.get_value("Sales Invoice", self.sales_invoice, "net_total")
			discount_amount = 0
			if self.discount_percent:
				discount_amount = self.total_actual_amount * (self.discount_percent/100)
			elif self.discount_amount:
				discount_amount = self.discount_amount
			self.total_amount_after_discount = self.total_actual_amount - discount_amount
			self.total_discounted_amount = discount_amount
		
		elif (
			self.apply_discount_on in ["Single Items", "Group of Items"]
			and self.sales_invoice
			and len(self.items) > 0
		):
			self.total_discounted_amount = 0
			self.total_actual_amount = 0
			self.total_amount_after_discount = 0
			for item in self.items:
				self.total_actual_amount += flt(item.actual_price)
				self.total_amount_after_discount += flt(item.amount_after_discount)
				self.total_discounted_amount += flt(item.discount_amount)
	


@frappe.whitelist()
def get_item_details(invoice_no, item_category, item_code):
	items = []
	invoice_doc = frappe.get_doc("Sales Invoice", invoice_no)
	for item in invoice_doc.items:
		if item.item_code == item_code:
			items.append({
				"item_category": item_category,
				"item_code": item.item_code,
				"item_name": item.item_name,
				"amount": item.amount,
				"si_detail": item.name,
				"sales_invoice": invoice_no,
			})

	return items

@frappe.whitelist()
def get_items(invoice_no, reference_dt=None, reset_options=None):
	items = []
	item_codes = []
	invoice_doc = frappe.get_doc("Sales Invoice", invoice_no)
	for item in invoice_doc.items:
		if (
			item.reference_dt and
			reference_dt and
			item.reference_dt == reference_dt
		):
			item_codes.append(item.item_code)
			items.append({
				"item_code": item.item_code,
				"item_name": item.item_name,
				"amount": item.amount,
				"reference_dt": item.reference_dt,
				"si_detail": item.name,
				"sales_invoice": invoice_no,
			})
		
		elif (
			not item.reference_dt and
			item.sales_order and
			reference_dt and
			reference_dt == "Drug Prescription"
		):
			item_codes.append(item.item_code)
			items.append({
				"item_code": item.item_code,
				"item_name": item.item_name,
				"amount": item.amount,
				"reference_dt": reference_dt,
				"si_detail": item.name,
				"sales_invoice": invoice_no,
			})

		elif (
			not item.reference_dt and
			not item.sales_order and
			reference_dt == "Other Items"
		):
			item_codes.append(item.item_code)
			items.append({
				"item_code": item.item_code,
				"item_name": item.item_name,
				"amount": item.amount,
				"reference_dt": reference_dt,
				"si_detail": item.name,
				"sales_invoice": invoice_no,
			})
		
		elif not reference_dt:
			item_group = None
			if not item.reference_dt and not item.sales_order:
				item_group = "Other Items"
			elif not item.reference_dt and item.sales_order:
				item_group = "Drug Prescription"

			item_codes.append(item.item_code)
			items.append({
				"item_code": item.item_code,
				"item_name": item.item_name,
				"amount": item.amount,
				"reference_dt": item.reference_dt or item_group,
				"si_detail": item.name,
				"sales_invoice": invoice_no,
			})
	
	if reset_options:
		return item_codes
	return items
