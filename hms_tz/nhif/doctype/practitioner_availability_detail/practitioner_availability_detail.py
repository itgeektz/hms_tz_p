# -*- coding: utf-8 -*-
# Copyright (c) 2020, Aakvatech and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document

class PractitionerAvailabilityDetail(Document):
	pass


def create_practitioner_availability_detail(pa_doc):
	'''
	return created doc in memory with the info from Practitioner Availability doc
	'''
	doc = frappe.new_doc('Practitioner Availability Detail')
	doc.practitioner_availability = pa_doc.name
	doc.availability_type = pa_doc.availability_type
	doc.availability = pa_doc.availability
	doc.practitioner = pa_doc.practitioner
	doc.healthcare_practitioner_name = pa_doc.healthcare_practitioner_name
	doc.from_date = pa_doc.from_date
	doc.from_time = pa_doc.from_time
	doc.to_date = pa_doc.to_date
	doc.to_time = pa_doc.to_time
	doc.repeat_this_event = pa_doc.repeat_this_event
	doc.present = pa_doc.present
	doc.appointment_type = pa_doc.appointment_type
	doc.duration = pa_doc.duration
	doc.service_unit = pa_doc.service_unit
	doc.total_service_unit_capacity = pa_doc.total_service_unit_capacity
	doc.color = pa_doc.color
	doc.out_patient_consulting_charge_item = pa_doc.out_patient_consulting_charge_item
	doc.op_consulting_charge = pa_doc.op_consulting_charge
	doc.inpatient_visit_charge_item = pa_doc.inpatient_visit_charge_item
	doc.inpatient_visit_charge = pa_doc.inpatient_visit_charge
	return doc


def delelte_all_related_practitioner_availability_detail(pa_doc):
	frappe.db.sql("DELETE FROM `tabPractitioner Availability Detail` WHERE practitioner_availability = '{0}'".format(pa_doc.name))