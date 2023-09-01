# Copyright (c) 2023, Aakvatech and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.utils import nowdate, nowtime, get_fullname

class NHIFTrackingClaimChange(Document):
	def update_nhif_track_record(self, item):
		self.quantity = item.item_quantity
		self.new_amount = item.amount_claimed
		self.amount_changed = self.previous_amount - item.amount_claimed

		self.save(ignore_permissions=True)

def track_changes_of_claim_items(claim):
	old_claim = claim.get_doc_before_save()

	list_of_item_codes = []
	for old_row in old_claim.nhif_patient_claim_item:
		for row in claim.nhif_patient_claim_item:
			if row.ref_docname not in list_of_item_codes:
				list_of_item_codes.append(row.ref_docname)
			
			if (
				old_row.item_code == row.item_code and
				old_row.ref_docname == row.ref_docname and
				old_row.amount_claimed != row.amount_claimed
			):
				item_exist = frappe.db.get_value("NHIF Tracking Claim Change", {
					"item_code": old_row.item_code,
					"nhif_patient_claim": claim.name,
					"ref_docname": old_row.ref_docname,
					"patient_encounter": old_row.patient_encounter
				})
				if item_exist:
					track_claim_doc = frappe.get_doc("NHIF Tracking Claim Change", item_exist)
					track_claim_doc.update_nhif_track_record(row)

				else:
					create_nhif_track_record(row, claim, old_row.amount_claimed, "Amount Changed")

	removed_items = [d for d in old_claim.nhif_patient_claim_item if d.ref_docname not in list_of_item_codes]
	for row in removed_items:
		create_nhif_track_record(row, claim, row.amount_claimed, "Item Removed")

def create_nhif_track_record(item, claim_doc, prev_amount, status):
	amount_changed = abs(prev_amount - item.amount_claimed)
	new_item = frappe.get_doc({
		"doctype": "NHIF Tracking Claim Change",
		"item_code": item.item_code,
		"item_name": item.item_name,
		"quantity": item.item_quantity,
		"claim_month": claim_doc.claim_month,
		"claim_year": claim_doc.claim_year,
		"company": claim_doc.company,
		"posting_date": nowdate(),
		"posting_time": nowtime(),
		"status": status,
		"previous_amount": prev_amount,
		"current_amount": item.amount_claimed,
		"amount_changed": abs(amount_changed),
		"nhif_patient_claim": item.parent,
		"patient_appointment": claim_doc.patient_appointment,
		"ref_docname": item.ref_docname,
		"patient_encounter": item.patient_encounter,
		"user_email": frappe.session.user,
		"edited_by": get_fullname()
	}).insert(ignore_permissions=True)