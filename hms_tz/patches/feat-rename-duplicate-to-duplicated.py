# Copyright (c) 2021, Aakvatech Limited and Contributors
# License: GNU General Public License v3. See license.txt

from __future__ import unicode_literals

import frappe

def execute():
	for encounter in frappe.db.sql_list("""select name from `tabPatient Encounter` where duplicate = 1 and duplicated != 1"""):
		frappe.set_value("Patient Encounter", encounter, "duplicated", 1)
	frappe.db.commit()