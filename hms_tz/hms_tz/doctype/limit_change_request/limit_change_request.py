import frappe
from frappe.utils import flt, nowdate, nowtime, cint, cstr, get_url_to_form
from frappe.model.document import Document
from erpnext.accounts.utils import get_balance_on


class LimitChangeRequest(Document):
<<<<<<< HEAD
    def validate(self):
        set_missing_values(self)

    def on_submit(self):
        if self.inpatient_record:
            frappe.db.set_value(
                "Inpatient Record", self.inpatient_record, "cash_limit", self.cash_limit
            )

            inpatient_record_doc = frappe.get_doc(
                "Inpatient Record", self.inpatient_record
            )

            if inpatient_record_doc.cash_limit == self.cash_limit:
                frappe.msgprint(
                    "Inpatient Record: {0} of Patient {1} - {2} has been updated with new cash limit: {3}".format(
                        frappe.bold(self.inpatient_record),
                        frappe.bold(self.patient),
                        frappe.bold(self.patient_name),
                        frappe.bold(self.cash_limit),
                    )
                )

    def on_cancel(self):
        old_cash_limit = frappe.get_value(
            "Patient", {"name": self.patient}, "cash_limit"
        )
        frappe.db.set_value(
            "Inpatient Record", self.inpatient_record, "cash_limit", old_cash_limit
        )


def set_missing_values(self):
    conditions = {}
    if self.patient:
        conditions["patient"] = self.patient
        conditions["docstatus"] = 1
=======
	def before_insert(self):
		self.set_missing_values()
	
	def after_insert(self):
		if self.is_cash_inpatient and self.inpatient_record:
			self.previous_cash_limit = frappe.get_value("Inpatient Record", self.inpatient_record, "cash_limit")

		if self.is_non_nhif_patient and self.appointment_no:
			self.previous_cash_limit = frappe.get_value("Patient Appointment", self.appointment_no, "daily_limit")
		
		if self.inpatient_record:
			self.current_total_deposit = -1 * (get_balance_on(
				party_type="Customer", party=self.patient_name, company=self.company
			))
		
		self.save()

	def validate(self):
		if self.is_cash_inpatient and self.is_non_nhif_patient:
			frappe.throw("You can't change Cash/Daily limit for both inpatient and non-nhif patient at the same time")

		if (
			self.appointment_no and
			self.company and
			self.company != frappe.get_value("Patient Appointment", self.appointment_no, "company")
		):
			frappe.throw("Company must be the same as the company of the appointment")
		
		self.validate_draft_duplicate()
	
	def validate_draft_duplicate(self):
		exists_lcr = frappe.get_value("Limit Change Request", {"name": ["!=", self.name], "docstatus": 0, "patient": self.patient, "company": self.company})
		if exists_lcr:
			url = get_url_to_form(self.doctype, exists_lcr)
			frappe.throw(f"There is a draft Limit Change Request: <a href='{url}'><b>{exists_lcr}</b></a> for this patient: <b>{self.patient}</b>, Use it instead")

	def before_submit(self):
		if not flt(self.cash_limit) or flt(self.cash_limit) == 0:
			frappe.throw("<b>Cash/Daily Limit is required</b>")
		
		if flt(self.previous_cash_limit) and flt(self.cash_limit) <= flt(self.previous_cash_limit):
			frappe.throw("New Cash/Daily Limit must be greater than the previous cash limit")
		
		self.approved_by = frappe.utils.get_fullname(frappe.session.user)

		if self.is_cash_inpatient and self.inpatient_record:
			frappe.db.set_value("Inpatient Record", self.inpatient_record, "cash_limit", self.cash_limit)
			
			inpatient_record_doc = frappe.get_doc("Inpatient Record", self.inpatient_record)

			if inpatient_record_doc.cash_limit == self.cash_limit:
				frappe.msgprint("Inpatient Record: {0} of Patient {1} - {2} has been updated with new cash limit: {3}".format(
					frappe.bold(self.inpatient_record),
					frappe.bold(self.patient),
					frappe.bold(self.patient_name),
					frappe.bold(self.cash_limit)
				))
		
		if (
			self.is_non_nhif_patient and 
			self.insurance_company and
			self.appointment_no
		):
			frappe.db.set_value("Patient Appointment", self.appointment_no, "daily_limit", self.cash_limit)
			frappe.msgprint(f"Daily Limit of: <b>{self.cash_limit}</b> was updated for Patient <b>{self.patient}</b>")

	def on_cancel(self):
		if self.is_cash_inpatient and self.inpatient_record:
			old_cash_limit = frappe.get_value("Patient", {"name": self.patient}, "cash_limit")
			frappe.db.set_value("Inpatient Record", self.inpatient_record, "cash_limit", old_cash_limit)
		
		if self.is_non_nhif_patient and self.appointment_no:
			insurance_subscription = frappe.get_value("Patient Appointment", {"name": self.appointment_no}, "insurance_subscription")
			coverage_plan = frappe.get_value("Healthcare Insurance Subscription", insurance_subscription, "healthcare_insurance_coverage_plan")
			old_daily_limit = frappe.get_value("Healthcare Insurance Coverage Plan", coverage_plan, "daily_limit")
			frappe.db.set_value("Patient Appointment", self.appointment_no, "daily_limit", old_daily_limit)

	def set_missing_values(self):
		conditions = {}
		if self.patient:
			conditions["patient"] = self.patient
		
		if self.company:
			conditions["company"] = self.company
			
		encounters = frappe.get_all("Patient Encounter", 
			filters=conditions, 
			fields=[
				"name", "encounter_date", "appointment", "inpatient_record",
				"mode_of_payment", "insurance_company"
	   		],
			order_by = "encounter_date desc",
			page_length=1
		)

		if encounters:
			self.appointment_no = encounters[0]["appointment"]
			self.inpatient_record = encounters[0]["inpatient_record"]
			if encounters[0]["mode_of_payment"]:
				self.is_cash_inpatient = 1
			else:
				self.is_non_nhif_patient = 1
				self.insurance_company = encounters[0]["insurance_company"]

		self.posting_date = nowdate()
		self.posting_time = nowtime()
		self.requested_by = frappe.utils.get_fullname(frappe.session.user)

>>>>>>> 142e43da (feat: allow limit change request to work for cash IPD and Non-NHIF insurance's patients (OPD and IPD))

    if self.company:
        conditions["company"] = self.company

    encounters = frappe.get_all(
        "Patient Encounter",
        filters=conditions,
        fields=["name", "encounter_date", "appointment", "inpatient_record"],
        order_by="encounter_date desc",
        page_length=1,
    )
    if encounters:
        self.appointment_no = encounters[0]["appointment"]
        self.inpatient_record = encounters[0]["inpatient_record"]
