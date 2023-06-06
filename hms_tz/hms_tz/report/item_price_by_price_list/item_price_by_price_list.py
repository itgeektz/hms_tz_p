# Copyright (c) 2023, Aakvatech and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
import pandas as pd
import numpy as np
import datetime as dt
import calendar
from frappe import _
from frappe.utils import cstr, cint, getdate
from frappe import msgprint, _

def execute(filters=None):
    columns = get_columns()
    data = []
    item_prices = get_item_prices(filters)

    if item_prices:
        colnames = [key for key in item_prices[0].keys()]
        # frappe.msgprint("colnames are: " + str(colnames))

        df = pd.DataFrame.from_records(item_prices, columns=colnames)
        # frappe.msgprint("dataframe columns are is: " + str(df.columns.tolist()))

        pvt = pd.pivot_table(
            df,
            values="price_list_rate",
            index=["template_name", "item_code", "status", "item_group"],
            columns="price_list",
            fill_value=0,
        )
        # frappe.msgprint(str(pvt))

        data = pvt.reset_index().values.tolist()
        # frappe.msgprint("Data is: " + str(data))

        # columns += pvt.columns.values.tolist()
        for column_name in pvt.columns.values.tolist():
            # frappe.msgprint("Column is: " + str(column_name))
            columns += [{"label": _(column_name), "fieldtype": "Float", "precision": 2}]
        # frappe.msgprint("Columns are: " + str(columns))

    return columns, data


def get_columns():
    columns = [
        {"label": _("Temlate Name"), "fieldname": "template_name", "width": 250},
        {
            "label": _("Item Code"),
            "fieldname": "item_code",
            "fieldtype": "Link",
            "options": "Item",
            "width": 250,
        },
        # {
        #     "label": _("Item Name"),
        #     "fieldname": "item_name",
        #     "width": 250
        # },
        {"label": _("Status"), "fieldname": "status", "width": 70},
        {"label": _("Item Group"), "fieldname": "item_group", "width": 150},
    ]
    return columns


def get_item_prices(filters):
    return frappe.db.sql(
        """ 
		SELECT  distinct temp.lab_test_name as template_name, 
				temp.lab_test_code as item_code, 
				if(temp.disabled = 0, "Active", "Disabled") as status,	
				temp.lab_test_group as item_group,
				IF(ip.price_list IS NULL, "NO PRICE", ip.price_list) as price_list,
				IF(ip.price_list IS NULL, 0, ip.price_list_rate) as price_list_rate,
				IF(ip.price_list IS NULL, "2020-01-01", ip.valid_from) as valid_from
		FROM `tabLab Test Template` temp LEFT JOIN `tabItem Price` ip ON temp.item = ip.item_code
		UNION
		SELECT  distinct temp.name as template_name, 
				temp.item_code as item_code, 
				if(temp.disabled = 0, "Active", "Disabled") as status,	
				temp.item_group as item_group,
				IF(ip.price_list IS NULL, "NO PRICE", ip.price_list) as price_list,
				IF(ip.price_list IS NULL, 0, ip.price_list_rate) as price_list_rate,
				IF(ip.price_list IS NULL, "2020-01-01", ip.valid_from) as valid_from
		FROM `tabRadiology Examination Template` temp LEFT JOIN `tabItem Price` ip ON temp.item = ip.item_code
		UNION
		SELECT  distinct temp.medication_name as template_name, 
				temp.item_code as item_code, 
				if(temp.disabled = 0, "Active", "Disabled") as status,	
				temp.item_group as item_group,
				IF(ip.price_list IS NULL, "NO PRICE", ip.price_list) as price_list,
				IF(ip.price_list IS NULL, 0, ip.price_list_rate) as price_list_rate,
				IF(ip.price_list IS NULL, "2020-01-01", ip.valid_from) as valid_from
		FROM `tabMedication` temp LEFT JOIN `tabItem Price` ip ON temp.item = ip.item_code
		UNION
		SELECT  distinct temp.therapy_type as template_name, 
				temp.item_code as item_code, 
				if(temp.disabled = 0, "Active", "Disabled") as status,	
				temp.item_group as item_group,
				IF(ip.price_list IS NULL, "NO PRICE", ip.price_list) as price_list,
				IF(ip.price_list IS NULL, 0, ip.price_list_rate) as price_list_rate,
				IF(ip.price_list IS NULL, "2020-01-01", ip.valid_from) as valid_from
		FROM `tabTherapy Type` temp LEFT JOIN `tabItem Price` ip ON temp.item = ip.item_code
		UNION
		SELECT  distinct temp.template as template_name, 
				temp.item_code as item_code, 
				if(temp.disabled = 0, "Active", "Disabled") as status,	
				temp.item_group as item_group,
				IF(ip.price_list IS NULL, "NO PRICE", ip.price_list) as price_list,
				IF(ip.price_list IS NULL, 0, ip.price_list_rate) as price_list_rate,
				IF(ip.price_list IS NULL, "2020-01-01", ip.valid_from) as valid_from
		FROM `tabClinical Procedure Template` temp LEFT JOIN `tabItem Price` ip ON temp.item = ip.item_code
		UNION
		SELECT  distinct temp.service_unit_type as template_name, 
				temp.item_code as item_code, 
				if(temp.disabled = 0, "Active", "Disabled") as status,	
				temp.item_group as item_group,
				IF(ip.price_list IS NULL, "NO PRICE", ip.price_list) as price_list,
				IF(ip.price_list IS NULL, 0, ip.price_list_rate) as price_list_rate,
				IF(ip.price_list IS NULL, "2020-01-01", ip.valid_from) as valid_from
		FROM `tabHealthcare Service Unit Type` temp LEFT JOIN `tabItem Price` ip ON temp.item = ip.item_code
		ORDER BY item_group, template_name ASC
	""",
        as_dict=1,
    )


# def get_item_prices(filters):
# 	return frappe.db.sql("""
# 		SELECT 	i.name as item_code,
# 				i.item_name,
# 				if(i.disabled = 0, "Active", "Disabled") as status,
# 				i.item_group,
# 				ip.price_list,
# 				ip.price_list_rate
# 		FROM `tabItem` i LEFT JOIN `tabItem Price` ip ON i.name = ip.item_code
# 		ORDER BY i.item_group, i.item_name ASC
# 	""", as_dict = 1)

