# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from . import __version__ as app_version

app_name = "hms_tz"
app_title = "HMS TZ"
app_publisher = "Aakvatech"
app_description = "HMS TZ"
app_icon = "octicon octicon-file-directory"
app_color = "grey"
app_email = "info@aakvatech.com"
app_license = "MIT"

fixtures = [
	{"doctype":"Custom Field", "filters": [["name", "in", (
		"Healthcare Insurance Claim-reference_dn",
		"Healthcare Insurance Claim-reference_dt",
		"Healthcare Insurance Company-default_price_list",
		"Healthcare Insurance Company-facility_code",
		"Healthcare Insurance Subscription-coverage_plan_card_number",
		"Healthcare Insurance Subscription-coverage_plan_name",
		"Healthcare Practitioner-doctors_signature",
		"Healthcare Practitioner-title_and_qualification",
		"Healthcare Practitioner-tz_mct_code",
		"Patient Appointment-authorization_number",
		"Patient Appointment-coverage_plan_card_number",
		"Patient Appointment-coverage_plan_name",
		"Patient Appointment-insurance_company_name",
		"Patient Appointment-ref_vital_signs",
		"Patient Appointment-reference_journal_entry",
		"Patient Appointment-referral_no",
		"Patient Encounter-examination_detail",
		"Patient-card_no",
		"Patient-column_break_3",
		"Patient-insurance_company",
		"Patient-insurance_details",
		"Patient-patient_details_with_formatting",
		"Payment Entry Reference-end_date",
		"Payment Entry Reference-posting_date",
		"Payment Entry Reference-section_break_9",
		"Payment Entry Reference-start_date",
		"Procedure Prescription-column_break_10",
		"Procedure Prescription-hso_payment_method",
		"Procedure Prescription-override_insurance_subscription",
		"Radiology Examination Template-body_part",
		"Radiology Examination Template-radiology_report",
		"Radiology Examination Template-radiology_report_details",
		"Radiology Examination Template-radiology_report_type",
		"Radiology Examination-body_part",
		"Radiology Examination-radiology_report",
		"Radiology Examination-radiology_report_details",
		"Vital Signs-oxygen_saturation_spo2",
		"Patient-product_code",
		"Patient-membership_no",
		"Patient Appointment-get_authorization_number",
		"Healthcare Service Order-prescribed",
		"Healthcare Service Insurance Coverage-maximum_claim_duration",
		"Healthcare Insurance Claim-section_break_40",
		"Healthcare Insurance Claim-ready_to_submit",
		"Healthcare Insurance Claim-column_break_38",
		"Healthcare Insurance Claim-insurance_company_item_name",
		"Healthcare Insurance Claim-insurance_company_item_code",
		"Healthcare Insurance Claim-section_break_35",
		"Patient Encounter-section_break_28",
		"Patient Encounter-patient_encounter_preliminary_diagnosis",
		"Patient Encounter-patient_encounter_final_diagnosis",
		"Drug Prescription-medical_code",
		"Lab Prescription-medical_code",
		"Procedure Prescription-medical_code",
		"Radiology Procedure Prescription-medical_code",
		"Therapy Plan Detail-medical_code",
		"Diet Recommendation-medical_code",
		"Patient Encounter-reference",
		"Patient Encounter-encounter_type",
		"Patient Encounter-duplicate",
		"Patient Encounter-column_break_31",
		"Patient Encounter-reference_encounter",
		"Patient Encounter-from_encounter",
		"Patient Encounter-previous_lab_prescription",
		"Patient Encounter-previous_drug_prescription",
		"Patient Encounter-previous_procedure_prescription",
		"Patient Encounter-previous_radiology_procedure_prescription",
		"Patient Encounter-previous_therapy_plan_detail",
		"Patient Encounter-previous_diet_recommendation",
		"Medication-default_comments",
		"Lab Test Template-lab_routine_normals",
		"Lab Test Template-m_text",
		"Lab Test Template-column_break_26",
		"Lab Test Template-f_text",
		"Lab Test Template-column_break_30",
		"Lab Test Template-c_min_range",
		"Lab Test Template-c_max_range",
		"Lab Test Template-c_text",
		"Lab Test Template-column_break_34",
		"Lab Test Template-i_min_range",
		"Lab Test Template-i_max_range",
		"Lab Test Template-i_text",
		"Lab Test Template-m_min_range",
		"Lab Test Template-m_max_range",
		"Lab Test Template-f_min_range",
		"Lab Test Template-f_max_range",
		"Normal Test Result-detailed_normal_range",
		"Normal Test Result-result_status",
		"Normal Test Result-min_normal",
		"Normal Test Result-max_normal",
		"Normal Test Result-text_normal"
		"Healthcare Insurance Claim-order_encounter",
		"Drug Prescription-override_subscription",
		"Lab Prescription-override_subscription",
		"Radiology Procedure Prescription-override_subscription",
		"Procedure Prescription-override_subscription",
		"Therapy Plan Detail-override_subscription",
		"Patient Encounter-section_break_52",
		"Patient Encounter-healthcare_service_unit",
		"Lab Prescription-prescribe",
		"Radiology Procedure Prescription-prescribe",
		"Procedure Prescription-prescribe",
		"Drug Prescription-prescribe",
		"Therapy Plan Detail-prescribe",
		"Delivery Note Item-reference_name",
		"Delivery Note Item-reference_doctype",
		"Delivery Note-reference_name",
		"Delivery Note-reference_doctype",
		"Healthcare Service Order-original_his",
		"Healthcare Service Order-clear_insurance_details",
		"Vital Signs-rbg",
		"Vital Signs-height_in_cm",
		"Therapy Plan Detail-comment",
		"Therapy Plan Detail-column_break_6",
		"Patient-next_to_kid_column_break",
		"Patient-next_to_kin_relationship",
		"Patient-next_to_kin_mobile_no",
		"Patient-next_to_kin_name",
		"Patient-next_to_kin_details",
		"Patient Encounter-image",
		"Vital Signs-image",
		"Patient Appointment-patient_image2",
		"Inpatient Record-patient_vitals",
		"Inpatient Record-patient_vitals_summary",
		"Inpatient Record-secondary_practitioner_name",
		"Inpatient Record-primary_practitioner_name",
		"Inpatient Record-practitioner_name",
		"Inpatient Record-previous_diet_recommendation",
		"Inpatient Record-previous_therapy_plan_detail",
		"Inpatient Record-previous_drug_prescription",
		"Inpatient Record-previous_clinical_procedures",
		"Inpatient Record-inpatient_record_final_diagnosis",
		"Inpatient Record-section_break_57",
		"Inpatient Record-previous_radiology_procedure",
		"Inpatient Record-previous_lab_tests",
		"Inpatient Record-inpatient_record_preliminary_diagnosis",
		"Inpatient Record-section_break_47",
		"Inpatient Record-duplicated_from",
		"Inpatient Record-reference_inpatient_record",
		"Inpatient Record-column_break_45",
		"Inpatient Record-duplicate",
		"Inpatient Record-inpatient_record_type",
		"Inpatient Record-reference",
		"Patient Encounter-blood_group",
		"Patient Encounter-symptoms_and_signs",
		"Patient Encounter-system_and_symptoms",
		"Patient Encounter Symptom-compliant_duration",
		"Patient Encounter Symptom-system",
		"Patient Appointment-nhif_patient_claim",
	)]]},
	{"doctype":"Property Setter", "filters": [["name", "in", (
		"Healthcare Insurance Subscription-main-search_fields",
		"Medication-main-search_fields",
		"Patient Appointment-radiology_examination_template-depends_on",
		"Patient-patient_details-hidden",
		"Radiology Examination Template-main-quick_entry",
		"Radiology Examination-tc_name-fetch_from",
		"Radiology Examination-tc_name-hidden",
		"Radiology Examination-terms-hidden",
		"Patient Appointment-naming_series-hidden",
		"Patient-main-quick_entry",
		"Patient Appointment-section_break_19-hidden",
		"Patient Encounter-diagnosis_in_print-hidden",
		"Patient Encounter-diagnosis-hidden",
		"Patient Encounter-physical_examination-hidden",
		"Patient Encounter-codification-hidden",
		"Patient Encounter-codification-collapsible",
		"Drug Prescription-comment-fetch_from",
		"Healthcare Service Insurance Coverage-is_active-allow_on_submit",
		"Healthcare Service Insurance Coverage-end_date-Allow on Submit",
		"Radiology Examination-appointment-hidden",
		"Lab Test-insurance_section-hidden",
		"Radiology Examination-insurance_section-hidden",
		"Drug Prescription-dosage-fetch_if_empty",
		"Drug Prescription-period-fetch_if_empty",
		"Drug Prescription-dosage_form-fetch_if_empty",
		"Patient Encounter-section_break_3-collapsible",
		"Patient Encounter-sb_source-collapsible,",
		"Patient Encounter-insurance_section-collapsible",
		"Patient Encounter-sb_test_prescription-collapsible",
		"Patient Encounter-radiology_procedures_section-collapsible",
		"Patient Encounter-sb_procedures-collapsible",
		"Patient Encounter-rehabilitation_section-collapsible",
		"Patient Encounter-diet_recommendation_section-collapsible",
		"Patient Encounter-encounter_comment-hidden",
		"Patient Encounter-rehabilitation_section-collapsible_depends_on",
		"Patient Encounter-sb_drug_prescription-collapsible_depends_on",
		"Patient Encounter-sb_procedures-collapsible_depends_on",
		"Patient Encounter-radiology_procedures_section-collapsible_depends_on",
		"Patient Encounter-sb_test_prescription-collapsible_depends_on",
		"Patient Encounter-source-read_only_depends_on",
		"Patient Encounter-company-read_only",
		"Patient Encounter-appointment_type-read_only_depends_on",
		"Patient-more_info-collapsible_depends_on",
		"Healthcare Insurance Subscription-country-hidden",
		"Healthcare Insurance Subscription-insurance_company_customer-hidden",
		"Healthcare Insurance Subscription-insurance_company_name-read_only",
		"Healthcare Insurance Subscription-gender-read_only",
		"Healthcare Insurance Subscription-customer-hidden",
		"Healthcare Insurance Subscription-patient_name-read_only",
		"Patient-default_price_list-hidden",
		"Patient-default_currency-read_only",
		"Patient-territory-hidden",
		"Patient-invite_user-default",
		"Patient-triage-hidden",
		"Drug Prescription-comment-mandatory_depends_on",
		"Procedure Prescription-comments-mandatory_depends_on",
		"Radiology Procedure Prescription-radiology_test_comment-mandatory_depends_on",
		"Lab Prescription-lab_test_comment-mandatory_depends_on",
		"Patient Encounter-main-image_field",
		"Vital Signs-main-image_field",
		"Patient Appointment-main-image_field",
		"Item-customer_details-collapsible_depends_on",
		"Item-customer_details-collapsible",
		"Healthcare Practitioner-main-search_fields",
		"Customer-main-search_fields",
		"Healthcare Practitioner-practitioner_name-in_global_search",
		"Inpatient Record-drug_prescription-permlevel",
		"Inpatient Record-encounter_details_section-collapsible",
		"Inpatient Record-company-read_only",
		"Inpatient Record-investigations_section-collapsible_depends_on",
		"Inpatient Record-radiology_orders_section-collapsible_depends_on",
		"Inpatient Record-rehabilitation_section-collapsible_depends_on",
		"Inpatient Record-medication_section-collapsible_depends_on",
		"Inpatient Record-procedures_section-collapsible_depends_on",
		"Inpatient Record-medication_section-collapsible",
		"Inpatient Record-diet_recommendation_section-collapsible",
		"Inpatient Record-rehabilitation_section-collapsible",
		"Inpatient Record-procedures_section-collapsible",
		"Inpatient Record-radiology_orders_section-collapsible",
		"Inpatient Record-investigations_section-collapsible",
		"Inpatient Record-diagnosis-hidden",
		"Inpatient Record-drug_prescription-label",
		"Inpatient Record-medication_section-label",
		"Inpatient Record-procedure_prescription-label"
		"Inpatient Record-procedures_section-label",
		"Inpatient Record-lab_test_prescription-label",
		"Inpatient Record-investigations_section-label",
		"Patient Encounter-sb_symptoms-hidden",
		"Patient Encounter-symptoms_in_print-hidden",
		"Patient-risk_factors-permlevel",
		"Patient-allergy_medical_and_surgical_history-permlevel",
		"Patient-personal_and_social_history-permlevel",
		"Appointment Type-main-sort_order",
		"Appointment Type-main-sort_field",
	)]]},
]

# Includes in <head>
# ------------------

# include js, css files in header of desk.html
# app_include_css = "/assets/hms_tz/css/hms_tz.css"
# app_include_js = "/assets/hms_tz/js/hms_tz.js"

# include js, css files in header of web template
# web_include_css = "/assets/hms_tz/css/hms_tz.css"
# web_include_js = "/assets/hms_tz/js/hms_tz.js"

# include custom scss in every website theme (without file extension ".scss")
# website_theme_scss = "hms_tz/public/scss/website"

# include js, css files in header of web form
# webform_include_js = {"doctype": "public/js/doctype.js"}
# webform_include_css = {"doctype": "public/css/doctype.css"}

# include js in page
# page_js = {"page" : "public/js/file.js"}

# include js in doctype views
doctype_js = {
	"Patient Appointment": "nhif/api/patient_appointment.js",
	"Patient": "nhif/api/patient.js",
	"Sales Invoice" : "nhif/api/sales_invoice.js",
	"Patient Encounter": "nhif/api/patient_encounter.js",
	"Lab Test": "nhif/api/lab_test.js",
	"Healthcare Service Order": "nhif/api/service_order.js",
	"Healthcare Insurance Company": "nhif/api/insurance_company.js",
	"Vital Signs": "nhif/api/vital_signs.js",
	"Inpatient Record": "nhif/api/inpatient_record.js",
}
#csf_tz.nhif.api.patient_appointment
# doctype_list_js = {"doctype" : "public/js/doctype_list.js"}
inpatient_record_list_js = {"doctype" : "nhif/api/inpatient_record_list.js"}
# doctype_tree_js = {"doctype" : "public/js/doctype_tree.js"}
# doctype_calendar_js = {"doctype" : "public/js/doctype_calendar.js"}

# Home Pages
# ----------

# application home page (will override Website Settings)
# home_page = "login"

# website user home page (by Role)
# role_home_page = {
#	"Role": "home_page"
# }

# Website user home page (by function)
# get_website_user_home_page = "hms_tz.utils.get_home_page"

# Generators
# ----------

# automatically create page for each record of this doctype
# website_generators = ["Web Page"]

# Installation
# ------------

# before_install = "hms_tz.install.before_install"
# after_install = "hms_tz.install.after_install"

# Desk Notifications
# ------------------
# See frappe.core.notifications.get_notification_config

# notification_config = "hms_tz.notifications.get_notification_config"

# Permissions
# -----------
# Permissions evaluated in scripted ways

# permission_query_conditions = {
# 	"Event": "frappe.desk.doctype.event.event.get_permission_query_conditions",
# }
#
# has_permission = {
# 	"Event": "frappe.desk.doctype.event.event.has_permission",
# }

# DocType Class
# ---------------
# Override standard doctype classes

# override_doctype_class = {
# 	"ToDo": "custom_app.overrides.CustomToDo"
# }

# Document Events
# ---------------
# Hook on document methods and events

doc_events = {
	"Patient Appointment": {
		"validate":[
			"hms_tz.nhif.api.patient_appointment.make_vital",
		]
	},
	"Vital Signs": {
		"on_submit":"hms_tz.nhif.api.patient_appointment.make_encounter",
	},
	"Patient": {
		"validate":"hms_tz.nhif.api.patient.validate",
	},
	"Healthcare Insurance Claim": {
		"before_insert":[
			"hms_tz.nhif.api.insurance_claim.set_patient_encounter",
			"hms_tz.nhif.api.insurance_claim.set_price",
		]
	},
	"Patient Encounter": {
		"validate":"hms_tz.nhif.api.patient_encounter.validate",
		"on_submit":"hms_tz.nhif.api.patient_encounter.on_submit",
	},
	"Healthcare Service Order": {
		"before_insert": "hms_tz.nhif.api.service_order.set_missing_values"
	},
}

# Scheduled Tasks
# ---------------

# scheduler_events = {
# 	"all": [
# 		"hms_tz.tasks.all"
# 	],
# 	"daily": [
# 		"hms_tz.tasks.daily"
# 	],
# 	"hourly": [
# 		"hms_tz.tasks.hourly"
# 	],
# 	"weekly": [
# 		"hms_tz.tasks.weekly"
# 	]
# 	"monthly": [
# 		"hms_tz.tasks.monthly"
# 	]
# }

# Testing
# -------

# before_tests = "hms_tz.install.before_tests"

# Overriding Methods
# ------------------------------
#
# override_whitelisted_methods = {
# 	"frappe.desk.doctype.event.event.get_events": "hms_tz.event.get_events"
# }
#
# each overriding function accepts a `data` argument;
# generated from the base implementation of the doctype dashboard,
# along with any modifications made in other Frappe apps
# override_doctype_dashboards = {
# 	"Task": "hms_tz.task.get_dashboard_data"
# }

# exempt linked doctypes from being automatically cancelled
#
# auto_cancel_exempted_doctypes = ["Auto Repeat"]

