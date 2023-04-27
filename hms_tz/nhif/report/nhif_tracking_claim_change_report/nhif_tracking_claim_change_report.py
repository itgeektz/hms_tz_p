# Copyright (c) 2023, Aakvatech and contributors
# For license information, please see license.txt

import frappe
from frappe import _


def execute(filters=None):
	parameters = get_conditions(filters)
	items = frappe.get_all("NHIF Tracking Claim Change", filters=parameters, fields=["*"])
	items_removed = len([d for d in items if d.status == "Item Removed"])
	items_amount_changed = len([h for h in items if h.status == "Amount Changed"])
	columns = get_columns(filters)
	data = []
	for row in items:
		row.update({
			"posting_datetime": str(row.posting_date) + " " + str(row.posting_time),
		})
		data.append(row)
	
	total_items = items_removed + items_amount_changed

	report_summary = [
		{
			"value": items_removed,
			"label": _("Items Removed"),
			"datatype": "Int",
		},
		{
			"value": items_amount_changed,
			"label": _("Item's Amount Changed"),
			"datatype": "Int",
		},
		{
			"value": total_items,
			"label": _("Total Items"),
			"datatype": "Int",
		}
	]
	
	return columns, data, None, None, report_summary


def get_conditions(filters):
	parameters = {}
	if filters.get("company"):
		parameters["company"] = filters.get("company")
	if filters.get("claim_month"):
		parameters["claim_month"] = filters.get("claim_month")
	if filters.get("claim_year"):
		parameters["claim_year"] = filters.get("claim_year")
	if filters.get("status"):
		parameters["status"] = filters.get("status")
	if filters.get("nhif_patient_claim"):
		parameters["nhif_patient_claim"] = filters.get("nhif_patient_claim")
	if filters.get("edited_by"):
		parameters["edited_by"] = filters.get("edited_by")
	
	return parameters

def get_columns(filters):
	columns = [
		{
			"fieldname": "posting_datetime",
			"label": "Date",
			"fieldtype": "Datetime",
			"width": 160
		},
		{
			"fieldname": "item_code",
			"label": "Item Code",
			"fieldtype": "Data",
			"width": 90
		},
		{
			"fieldname": "item_name",
			"label": "Item Name",
			"fieldtype": "Data",
			"width": 150
		},
		{
			"fieldname": "quantity",
			"label": "Qty",
			"fieldtype": "Int",
			"width": 50
		},
		{
			"fieldname": "previous_amount",
			"label": "Previous Amount",
			"fieldtype": "Currency",
			"width": 110
		},
		{
			"fieldname": "current_amount",
			"label": "Current Amount",
			"fieldtype": "Currency",
			"width": 110
		},
		{
			"fieldname": "amount_changed",
			"label": "Amount Changed",
			"fieldtype": "Currency",
			"width": 110
		},
		{
			"fieldname": "status",
			"label": "Status",
			"fieldtype": "Data",
			"width": 130
		},
		{
			"fieldname": "nhif_patient_claim",
			"label": "NHIF Patient Claim",
			"fieldtype": "Link",
			"options": "NHIF Patient Claim",
			"width": 150
		},
		{
			"fieldname": "patient_appointment",
			"label": "Patient Appointment",
			"fieldtype": "Link",
			"options": "Patient Appointment",
			"width": 150
		},
		{
			"fieldname": "patient_encounter",
			"label": "Patient Encounter",
			"fieldtype": "Link",
			"options": "Patient Encounter",
			"width": 150
		},
		{
			"fieldname": "edited_by",
			"label": "Edited By",
			"fieldtype": "Data",
			"width": 150
		},
		{
			"fieldname": "comment",
			"label": "Comment",
			"fieldtype": "Data",
			"width": 200
		},
	]
	
	return columns