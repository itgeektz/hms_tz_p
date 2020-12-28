// Copyright (c) 2015, Frappe Technologies Pvt. Ltd. and Contributors
// License: GNU General Public License v3. See license.txt

frappe.views.calendar["Practitioner Availability Detail"] = {
	field_map: {
		"start": "from_date",
		"end": "to_date",
		"id": "name",
		"title": "healthcare_practitioner_name",
		"status": 'availability_type',
		"color": 'color',
	},
	style_map: {
        Public: 'success',
        Private: 'info'
    },

	fields: ["from_date", "availability", "from_time", "to_time", "availability_type", "name", "healthcare_practitioner_name", "color"],
	get_events_method: "hms_tz.nhif.doctype.practitioner_availability_detail.practitioner_availability_detail.get_events",
}
