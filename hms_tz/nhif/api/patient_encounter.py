# -*- coding: utf-8 -*-
# Copyright (c) 2020, Aakvatech and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe import _
import json
from frappe.utils import (
    nowdate,
    getdate,
    nowtime,
    cint,
    cstr,
    flt,
    date_diff,
)
from hms_tz.nhif.api.healthcare_utils import (
    get_item_rate,
    get_warehouse_from_service_unit,
    get_item_price,
    create_individual_lab_test,
    create_individual_radiology_examination,
    create_individual_procedure_prescription,
    msgThrow,
    msgPrint,
    validate_nhif_patient_claim_status,
)
from healthcare.healthcare.doctype.healthcare_settings.healthcare_settings import (
    get_receivable_account,
    get_income_account,
)
import time
from hms_tz.nhif.api.patient_appointment import (
    get_mop_amount,
    get_discount_percent,
    calculate_patient_age,
)
from erpnext.accounts.utils import get_balance_on


def on_trash(doc, method):
    pmr_list = frappe.get_all(
        "Patient Medical Record",
        fields={"name"},
        filters={
            "reference_doctype": "Patient Encounter",
            "reference_name": doc.name,
        },
    )
    for pmr_doc in pmr_list:
        frappe.delete_doc(
            "Patient Medical Record", pmr_doc.name, ignore_permissions=True
        )


def before_insert(doc, method):
    doc.encounter_date = nowdate()
    doc.encounter_time = nowtime()

    if doc.insurance_company and "NHIF" in doc.insurance_company:
        validate_nhif_patient_claim_status(
            "Patient Encounter", doc.company, doc.appointment, doc.insurance_company
        )


# regency rock: 95
def after_insert(doc, method):
    if doc.company and doc.mode_of_payment:
        pharmacy_details = frappe.get_value(
            "Company",
            doc.company,
            [
                "auto_set_pharmacy_on_patient_encounter",
                "opd_cash_pharmacy",
                "ipd_cash_pharmacy",
            ],
            as_dict=1,
        )

        if (
            pharmacy_details
            and pharmacy_details.auto_set_pharmacy_on_patient_encounter == 1
        ):
            if doc.inpatient_record:
                if not pharmacy_details.ipd_cash_pharmacy:
                    frappe.throw(
                        _(
                            f"<b>Please set IPD Cash Pharmacy in Company: <b>{doc.company}</b> to allow auto set of pharmacy</b>"
                        )
                    )
                doc.default_healthcare_service_unit = pharmacy_details.ipd_cash_pharmacy
            else:
                if not pharmacy_details.opd_cash_pharmacy:
                    frappe.throw(
                        _(
                            f"<b>Please set OPD Cash Pharmacy in Company: <b>{doc.company}</b>  to allow auto set of pharmacy</b>"
                        )
                    )
                doc.default_healthcare_service_unit = pharmacy_details.opd_cash_pharmacy

    if doc.insurance_coverage_plan:
        pharmacy_details = frappe.get_value(
            "Healthcare Insurance Coverage Plan",
            doc.insurance_coverage_plan,
            [
                "auto_set_pharmacy_on_patient_encounter",
                "opd_insurance_pharmacy",
                "ipd_insurance_pharmacy",
            ],
            as_dict=1,
        )

        if (
            pharmacy_details
            and pharmacy_details.auto_set_pharmacy_on_patient_encounter == 1
        ):
            if doc.inpatient_record:
                if not pharmacy_details.ipd_insurance_pharmacy:
                    frappe.throw(
                        _(
                            f"<b>Please set IPD Insurance Pharmacy in Healthcare Insurance Coverage Plan: <b>{doc.insurance_coverage_plan}</b> to allow auto set of pharmacy</b>"
                        )
                    )
                doc.default_healthcare_service_unit = (
                    pharmacy_details.ipd_insurance_pharmacy
                )
            else:
                if not pharmacy_details.opd_insurance_pharmacy:
                    frappe.throw(
                        _(
                            f"<b>Please set OPD Insurance Pharmacy in Healthcare Insurance Coverage Plan: <b>{doc.insurance_coverage_plan}</b> to allow auto set of pharmacy</b>"
                        )
                    )
                doc.default_healthcare_service_unit = (
                    pharmacy_details.opd_insurance_pharmacy
                )
    set_price_list(doc)
    doc.save()


def set_price_list(doc):
    price_list = None
    if doc.insurance_subscription:
        hic_plan = frappe.get_cached_value(
            "Healthcare Insurance Subscription",
            doc.insurance_subscription,
            "healthcare_insurance_coverage_plan",
        )
        price_list = frappe.get_cached_value(
            "Healthcare Insurance Coverage Plan", hic_plan, "price_list"
        )
    elif doc.mode_of_payment:
        price_list = frappe.get_cached_value(
            "Mode of Payment", doc.mode_of_payment, "price_list"
        )
    if price_list:
        doc.price_list = price_list


def on_submit_validation(doc, method):
    child_tables = {
        "lab_test_prescription": "lab_test_code",
        "radiology_procedure_prescription": "radiology_examination_template",
        "procedure_prescription": "procedure",
        "drug_prescription": "drug_code",
        "therapies": "therapy_type",
        # "diet_recommendation": "diet_plan" dosent have Healthcare Service Insurance Coverage
    }
    if doc.encounter_type == "Initial":
        doc.reference_encounter = doc.name

    if not doc.healthcare_package_order:
        show_last_prescribed(doc, method)
        show_last_prescribed_for_lrpt(doc, method)

    checkـforـduplicate(doc, method)

    childs_map = [
        {
            "table": "lab_test_prescription",
            "doctype": "Lab Test Template",
            "item": "lab_test_code",
        },
        {
            "table": "radiology_procedure_prescription",
            "doctype": "Radiology Examination Template",
            "item": "radiology_examination_template",
        },
        {
            "table": "procedure_prescription",
            "doctype": "Clinical Procedure Template",
            "item": "procedure",
        },
        {
            "table": "drug_prescription",
            "doctype": "Medication",
            "item": "drug_code",
        },
        {
            "table": "therapies",
            "doctype": "Therapy Type",
            "item": "therapy_type",
        },
    ]
    for child in childs_map:
        for row in doc.get(child.get("table")):
            healthcare_doc = frappe.get_doc(
                child.get("doctype"), row.get(child.get("item"))
            )
            if healthcare_doc.disabled:
                msgThrow(
                    _(
                        f"{child.get('doctype')}: <b>{row.get(child.get('item'))}</b> selected at Row#: {row.idx} is <b>disabled</b>. Please select an enabled item."
                    ),
                    method,
                )
            company_option = None
            for option in healthcare_doc.company_options:
                if doc.company == option.company:
                    company_option = option.company

                    if (
                        child.get("doctype") != "Medication"
                        and row.doctype != "Drug Prescription"
                    ):
                        row.department_hsu = option.service_unit

            if not company_option:
                msgThrow(
                    _(
                        "No company option found for template: {0} and company: {1}".format(
                            frappe.bold(row.get(child.get("item"))),
                            frappe.bold(doc.company),
                        )
                    ),
                    method,
                )

            if (
                child.get("doctype") == "Clinical Procedure Template"
                and row.doctype == "Procedure Prescription"
            ):
                if healthcare_doc.is_inpatient and not doc.inpatient_record:
                    msgThrow(
                        _(
                            "<h4>This Procedure: <strong>{0}</strong> is allowed for Admitted Patient only</h4>"
                        ).format(frappe.bold(row.get(child.get("item")))),
                        method,
                    )
            if (
                child.get("doctype") == "Medication"
                and row.doctype == "Drug Prescription"
            ):
                if (
                    doc.insurance_subscription
                    and healthcare_doc.medication_category == "Category S Medication"
                ):
                    frappe.msgprint(
                        f"Item: {row.get(child.get('item'))} is Category S Medication",
                        alert=True,
                    )

                # auto calculating quantity
                if not row.quantity:
                    row.quantity = get_drug_quantity(row)

    # Run on_submit?
    prescribed_list = ""
    for key, value in child_tables.items():
        table = doc.get(key)
        for row in table:
            quantity = 0
            row_item = row.get("drug_code") or row.get("therapy_type")
            if row_item:
                quantity += cint(row.get("quantity")) or cint(row.get("no_of_sessions"))

                if not quantity:
                    frappe.throw(
                        _(
                            "Quantity for Item: {0}, Row: {1} can not be zero".format(
                                frappe.bold(row_item), frappe.bold(row.idx)
                            )
                        )
                    )

            if (
                (not doc.insurance_subscription)
                or row.prescribe
                or row.is_not_available_inhouse
            ):
                row.prescribe = 1
                prescribed_list += "-  <b>" + row.get(value) + "</b><BR>"
                if row.is_not_available_inhouse:
                    prescribed_list += " - THIS ITEM IS NOT AVAILABLE INHOUSE "
                prescribed_list += "<BR>"
            elif not row.prescribe:
                if row.get("no_of_sessions") and doc.insurance_subscription:
                    if row.no_of_sessions != 1:
                        row.no_of_sessions = 1
                        frappe.msgprint(
                            _(
                                "No of sessions have been set to 1 for {0} as per"
                                " insurance rules."
                            ).format(row.get(value)),
                            alert=True,
                        )
            # if not row.is_not_available_inhouse:
	    #	old_method = method
            #   if doc.insurance_subscription and not row.prescribe:
            #          method = "validate"
           #      validate_stock_item(
            #         row.get(value),
            #        quantity,
             #        doc.company,
              #       row.get("prescribe"),
               #      healthcare_service_unit=row.get("healthcare_service_unit"),
                #     method=method,
                # )
              #   if doc.insurance_subscription:
             #        method = old_method

    if prescribed_list and not doc.healthcare_package_order:
        msgPrint(
            _(
                "{0}<BR>The above been prescribed. <b>Request the patient to visit the"
                " cashier for billing/cash payment</b> or prescription printout."
            ).format(prescribed_list),
            method,
        )

    # Run on_submit
    # mtuha_missing = ""
    # for final_diagnosis in doc.patient_encounter_final_diagnosis:
    #     if not final_diagnosis.mtuha:
    #         mtuha_missing += "-  <b>" + final_diagnosis.medical_code + "</b><br>"

    # if mtuha_missing:
    #     frappe.msgprint(
    #         _("{0}<br>MTUHA Code not defined for the above diagnosis").format(
    #             mtuha_missing
    #         ), alert=True
    #     )

    if not doc.patient_age:
        doc.patient_age = calculate_patient_age(doc.patient)

    validate_medical_code(doc, method)

    # shm rock: 151
    set_practitioner_name(doc, method)

    insurance_subscription = doc.insurance_subscription
    if not insurance_subscription:
        return

    if not doc.healthcare_service_unit and not doc.healthcare_package_order:
        frappe.throw(_("Healthcare Service Unit not set"))
    healthcare_insurance_coverage_plan = frappe.get_cached_value(
        "Healthcare Insurance Subscription",
        insurance_subscription,
        "healthcare_insurance_coverage_plan",
    )
    if not healthcare_insurance_coverage_plan:
        frappe.throw(_("Healthcare Insurance Coverage Plan is Not defiend"))
    today = nowdate()
    healthcare_service_templates = {}
    for key, value in child_tables.items():
        for row in doc.get(key):
            if row.override_subscription or row.prescribe:
                continue

            # healthcare_service_templates is like {"CBC": [cbc1_lab_prescription_line_object, cbc2_lab_prescription_line_object], "XRay Abdomen": [radiology_prescription_line_object], ["Panadol": drug_prescription_line_object]}
            rows_affected = healthcare_service_templates.setdefault(row.get(value), [])
            rows_affected.append(row)
    # hsic => Healthcare Service Insurance Coverage
    hsic_list = frappe.get_all(
        "Healthcare Service Insurance Coverage",
        fields={
            "healthcare_service_template",
            "maximum_number_of_claims",
            "approval_mandatory_for_claim",
        },
        filters={
            "is_active": 1,
            "healthcare_insurance_coverage_plan": healthcare_insurance_coverage_plan,
            "start_date": ("<=", today),
            "end_date": (">=", today),
            "healthcare_service_template": ("in", healthcare_service_templates),
        },
        order_by="modified desc",
    )
    # hsic_map is like {"CBC": HSIC_object_for_CBC, "XRay Abdomen": HSIC_object_for_xray_abdomen, "Panadol": HSIC_object_for_panadol}
    hsic_map = {hsic.healthcare_service_template: hsic for hsic in hsic_list}
    hicp_name, is_exclusions = frappe.get_cached_value(
        "Healthcare Insurance Coverage Plan",
        healthcare_insurance_coverage_plan,
        ["coverage_plan_name", "is_exclusions"],
    )
    for template in healthcare_service_templates:
        if not is_exclusions:
            if template not in hsic_map:
                for row_item in healthcare_service_templates[template]:
                    if (
                        doc.company
                        and frappe.get_cached_value(
                            "Company",
                            doc.company,
                            "auto_prescribe_items_on_patient_encounter",
                        )
                        == 1
                    ):
                        row_item.prescribe = 1

                msg = _(
                    f"{template} <h4 style='background-color:LightCoral'>NOT COVERED</h4> in Healthcare Insurance Coverage Plan {str(hicp_name)} plan.<br>Patient should pay cash for this service"
                )
                msgThrow(
                    msg,
                    method,
                )
                continue
        else:
            if template in hsic_map:
                for row_item in healthcare_service_templates[template]:
                    if (
                        doc.company
                        and frappe.get_cached_value(
                            "Company",
                            doc.company,
                            "auto_prescribe_items_on_patient_encounter",
                        )
                        == 1
                    ):
                        row_item.prescribe = 1

                msg = _(
                    f"{template} <h4 style='background-color:LightCoral'>NOT COVERED</h4> in Healthcare Insurance Coverage Plan {str(hicp_name)} plan.<br>Patient should pay cash for this service"
                )
                msgThrow(
                    msg,
                    method,
                )
            continue

        coverage_info = hsic_map[template]
        for row in healthcare_service_templates[template]:
            row.is_restricted = coverage_info.approval_mandatory_for_claim
            if row.is_restricted:
                frappe.msgprint(
                    _("{0} with template {1} requires additional authorization").format(
                        _(row.doctype), template
                    ),
                    alert=True,
                )
        if coverage_info.maximum_number_of_claims == 0:
            continue

    validate_totals(doc, method)


def checkـforـduplicate(doc, method):
    items = []
    for item in doc.drug_prescription:
        if item.drug_code not in items:
            items.append(item.drug_code)
        else:
            msgThrow(
                _("Drug '{0}' is duplicated in line '{1}' in Drug Prescription").format(
                    item.drug_code, item.idx
                ),
                method,
            )


@frappe.whitelist()
def duplicate_encounter(encounter):
    doc = frappe.get_doc("Patient Encounter", encounter)
    if doc.healthcare_package_order:
        frappe.throw(
            _(
                "Cannot duplicate an encounter of healthcare package order, Please let the patient to create appointment again"
            )
        )
    if doc.insurance_company and "NHIF" in doc.insurance_company:
        validate_nhif_patient_claim_status(
            "Patient Encounter", doc.company, doc.appointment, doc.insurance_company
        )

    if not doc.docstatus == 1 or doc.encounter_type == "Final" or doc.duplicated == 1:
        frappe.msgprint(
            _(
                "This encounter cannot be duplicated. Check if it is already duplicated"
                " using Menu/Links."
            ),
            alert=True,
        )
        return
    encounter_doc = frappe.copy_doc(doc)
    encounter_dict = encounter_doc.as_dict()
    child_tables = {
        "drug_prescription": "previous_drug_prescription",
        "lab_test_prescription": "previous_lab_prescription",
        "procedure_prescription": "previous_procedure_prescription",
        "radiology_procedure_prescription": "previous_radiology_procedure_prescription",
        "therapies": "previous_therapy_plan_detail",
        "diet_recommendation": "previous_diet_recommendation",
    }

    # Copy the examination detail from previous encounter before clearing it
    clinical_notes = (
        cstr(encounter_dict["hms_tz_previous_examination_detail"])
        + "\n"
        + cstr(encounter_dict["examination_detail"])
    )

    fields_to_clear = [
        "name",
        "owner",
        "creation",
        "modified",
        "modified_by",
        "docstatus",
        "amended_from",
        "amendment_date",
        "parentfield",
        "parenttype",
        "sales_invoice",
        "is_not_billable",
    ]

    for key, value in child_tables.items():
        cur_table = encounter_dict.get(key)
        if not cur_table:
            continue
        for row in cur_table:
            new_row = row
            for fieldname in fields_to_clear:
                new_row[fieldname] = None
            encounter_dict[value].append(new_row)
        encounter_dict[key] = []
    encounter_dict["duplicated"] = 0
    encounter_dict["examination_detail"] = ""
    encounter_dict["hms_tz_previous_examination_detail"] = clinical_notes

    encounter_dict["encounter_type"] = "Ongoing"
    if not encounter_dict.get("reference_encounter"):
        encounter_dict["reference_encounter"] = doc.name
    encounter_dict["from_encounter"] = doc.name
    encounter_dict["previous_total"] = doc.previous_total + doc.current_total
    encounter_dict["current_total"] = 0
    encounter_dict["encounter_date"] = nowdate()
    encounter_dict["encounter_time"] = nowtime()
    encounter_doc = frappe.get_doc(encounter_dict)
    encounter_doc.save(ignore_permissions=True)
    frappe.msgprint(_("Patient Encounter {0} created".format(encounter_doc.name)))
    frappe.db.update(doc.doctype, doc.name, {"duplicated": 1})
    return encounter_doc.name


def get_item_info(item_code=None, medication_name=None):
    data = {}
    if not item_code and medication_name:
        item_code = frappe.get_cached_value("Medication", medication_name, "item")
    if item_code:
        is_stock, disabled = frappe.get_cached_value(
            "Item", item_code, ["is_stock_item", "disabled"]
        )
        data = {"item_code": item_code, "is_stock": is_stock, "disabled": disabled}
    return data


def get_stock_availability(item_code, warehouse):
    latest_sle = frappe.db.sql(
        """SELECT qty_after_transaction AS actual_qty
        FROM `tabStock Ledger Entry`
        WHERE item_code = %s AND warehouse = %s
          AND is_cancelled = 0
        ORDER BY creation DESC
        LIMIT 1""",
        (item_code, warehouse),
        as_dict=1,
    )

    sle_qty = latest_sle[0].actual_qty or 0 if latest_sle else 0
    return sle_qty


@frappe.whitelist()
def validate_stock_item(
    healthcare_service,
    qty,
    company,
    prescribe,
    warehouse=None,
    healthcare_service_unit=None,
    caller="Unknown",
    method=None,
):
    setting_doc = frappe.get_cached_doc("Healthcare Settings")
    if caller == "Drug Prescription":
        method = "validate"

    elif prescribe == 0:
        if setting_doc.only_alert_if_less_stock_of_drug_item_for_insurance_in_pe == 1:
            method = "validate"
        elif (
            setting_doc.stop_encounter_if_less_stock_of_drug_item_for_insurance_in_pe
            == 1
        ):
            method = method
        # else:
        #     frappe.throw(
        #         "<b>Please set the stock validation method (either only alert or stop when less stock) in Healthcare Settings for Insurance Patients</b>"
        #     )

    elif prescribe == 1:
        if setting_doc.only_alert_if_less_stock_of_drug_item_for_cash_in_pe == 1:
            method = "validate"
        elif setting_doc.stop_encounter_if_less_stock_of_drug_item_for_cash_in_pe == 1:
            method = method
        # else:
        #     frappe.throw(
        #         "<b>Please set the stock validation method (either only alert or stop when less stock) in Healthcare Settings for Cash Patients</b>"
        #     )

    if caller != "Drug Prescription" and not healthcare_service_unit:
        return

    qty = float(qty or 0)
    if qty == 0:
        qty = 1

    item_info = get_item_info(medication_name=healthcare_service)
    stock_qty = 0
    if healthcare_service_unit:
        warehouse = get_warehouse_from_service_unit(healthcare_service_unit)
        # frappe.msgprint(_("{0} selected using {1}").format(warehouse, healthcare_service_unit), alert=True)
    if not warehouse:
        msgThrow(
            _(
                "Warehouse is missing in healthcare service unit {0} when checking"
                " for {1}"
            ).format(healthcare_service_unit, item_info.get("item_code")),
            method,
        )
    if item_info.get("is_stock") and item_info.get("item_code"):
        stock_qty = get_stock_availability(item_info.get("item_code"), warehouse) or 0
        if float(qty) > float(stock_qty):
            # To be removed after few months of stability. 2021-03-18 17:01:46
            # This is to avoid socketio diconnection when bench is restarted but user session is on.
            msgThrow(
                _(
                    f"Available quantity for item: <h4 style='background-color:\
                    LightCoral'>{item_info.get('item_code')} is {stock_qty}</h4>In {warehouse}/{healthcare_service_unit}."
                ),
                method,
            )
            return False
    # if stock_qty > 0:
    #     frappe.msgprint(_("Available quantity for the item {0} in {1}/{2} is {3} pcs.").format(
    #         healthcare_service, warehouse, healthcare_service_unit, stock_qty), alert=True)
    return True


def on_submit(doc, method):
    if (
        not doc.insurance_subscription
        and doc.inpatient_record
        and not doc.healthcare_package_order
    ):  # Cash inpatient billing
        inpatient_billing(doc, method)
    else:  # insurance patient
        on_submit_validation(doc, method)
        create_healthcare_docs(doc, method)
        create_delivery_note(doc, method)

    if (
        doc.healthcare_package_order
        and not doc.insurance_subscription
        and not doc.inpatient_record
    ):
        create_items_from_healthcare_package_orders(doc, method)

    if doc.inpatient_record:
        update_inpatient_record_consultancy(doc)


@frappe.whitelist()
def create_healthcare_docs_from_name(patient_encounter_doc_name):
    patient_encounter_doc = frappe.get_doc(
        "Patient Encounter", patient_encounter_doc_name
    )
    create_healthcare_docs(patient_encounter_doc, "from_button")
    create_delivery_note(patient_encounter_doc, "from_button")


def create_healthcare_docs(patient_encounter_doc, method="event"):
    encounter_list = frappe.get_list(
        "Patient Encounter",
        filters={"reference_encounter": patient_encounter_doc.reference_encounter},
    )
    for encounter in encounter_list:
        # frappe.msgprint(
        #     _("Patient Encounter {0} being processed.").format(encounter.name)
        # )
        create_healthcare_docs_per_encounter(
            frappe.get_doc("Patient Encounter", encounter)
        )
    if method == "from_button":
        frappe.msgprint(
            _(
                "The {0} patient encounters were processed for creating pending healthcare docs."
            ).format(str(len(encounter_list)))
        )


def create_healthcare_docs_per_encounter(patient_encounter_doc):
    if patient_encounter_doc.docstatus != 1:
        frappe.msgprint(
            _(
                "Cannot process Patient Encounter that is not submitted! Please submit"
                " and try again."
            ),
            alert=True,
        )
        return
    if not patient_encounter_doc.appointment:
        frappe.msgprint(
            _(
                "Patient Encounter does not have patient appointment number! Request"
                " for support with this message."
            ),
            alert=True,
        )
        return
    if (
        not patient_encounter_doc.insurance_subscription
        and not patient_encounter_doc.inpatient_record
    ):
        return

    child_tables_list = [
        "lab_test_prescription",
        "radiology_procedure_prescription",
        "procedure_prescription",
    ]
    for child_table_field in child_tables_list:
        if patient_encounter_doc.get(child_table_field):
            child_table = patient_encounter_doc.get(child_table_field)
            for child in child_table:
                if patient_encounter_doc.insurance_subscription and child.prescribe:
                    continue

                if (
                    child.is_cancelled
                    or child.is_not_available_inhouse
                    or child.hms_tz_is_limit_exceeded
                ):
                    continue

                if child.doctype == "Lab Prescription":
                    create_individual_lab_test(patient_encounter_doc, child)
                elif child.doctype == "Radiology Procedure Prescription":
                    create_individual_radiology_examination(
                        patient_encounter_doc, child
                    )
                elif child.doctype == "Procedure Prescription":
                    create_individual_procedure_prescription(
                        patient_encounter_doc, child
                    )


def create_delivery_note(patient_encounter_doc, method):
    encounter_list = frappe.get_list(
        "Patient Encounter",
        filters={"reference_encounter": patient_encounter_doc.reference_encounter},
    )
    for encounter in encounter_list:
        create_delivery_note_per_encounter(
            frappe.get_doc("Patient Encounter", encounter), method
        )
    if method == "from_button":
        frappe.msgprint(
            _(
                "The {0} patient encounters were processed for creating pending delivery notes."
            ).format(str(len(encounter_list)))
        )


def create_delivery_note_per_encounter(patient_encounter_doc, method):
    if not patient_encounter_doc.appointment:
        return
    if (
        not patient_encounter_doc.insurance_subscription
        and not patient_encounter_doc.inpatient_record
        and not patient_encounter_doc.healthcare_package_order
    ):
        return
    # Create list of warehouses to process delivery notes by warehouses
    warehouses = []
    for line in patient_encounter_doc.drug_prescription:
        if line.invoiced and line.prescribe:
            frappe.msgprint(_("Invoiced and Prescribed patient who is an inpatient"))
        elif patient_encounter_doc.insurance_subscription and line.prescribe:
            continue
        if (
            line.drug_prescription_created
            or line.is_not_available_inhouse
            or line.is_cancelled
            or line.hms_tz_is_limit_exceeded
        ):
            continue
        item_code = frappe.get_cached_value("Medication", line.drug_code, "item")
        if not item_code:
            frappe.throw(
                _(
                    f"The Item Code for {line.drug_code} is not found!<br>Please request administrator to set item code in {line.drug_code}."
                )
            )
        is_stock = frappe.get_cached_value("Item", item_code, "is_stock_item")
        if not is_stock:
            continue
        warehouse = get_warehouse_from_service_unit(line.healthcare_service_unit)
        if warehouse and warehouse not in warehouses:
            warehouses.append(warehouse)

    # apply discount if it is available on Heathcare Insurance Company
    discount_percent = 0
    if (
        patient_encounter_doc.insurance_company
        and "NHIF" not in patient_encounter_doc.insurance_company
    ):
        discount_percent = get_discount_percent(patient_encounter_doc.insurance_company)

    # Process list of warehouses
    for element in warehouses:
        items = []
        for row in patient_encounter_doc.drug_prescription:
            if (
                row.drug_prescription_created
                or row.is_not_available_inhouse
                or row.is_cancelled
                or row.hms_tz_is_limit_exceeded
            ):
                continue
            encounter_customer = ""
            if row.invoiced and row.prescribe:
                encounter_customer = frappe.get_cached_value(
                    "Patient", patient_encounter_doc.patient, "customer"
                )
                insurance_coverage_plan = ""
            elif patient_encounter_doc.insurance_subscription and row.prescribe:
                continue
            warehouse = get_warehouse_from_service_unit(row.healthcare_service_unit)
            if element != warehouse:
                continue
            item_code = frappe.get_cached_value("Medication", row.drug_code, "item")
            if not item_code:
                frappe.throw(
                    _(
                        f"The Item Code for {row.drug_code} is not found!<br>Please request administrator to set item code in {row.drug_code}."
                    )
                )

            is_stock, item_name = frappe.get_cached_value(
                "Item", item_code, ["is_stock_item", "item_name"]
            )
            if not is_stock:
                continue
            if not item_code:
                frappe.throw(
                    _(
                        f"The Item Code for {row.drug_code} is not found!<br>Please request administrator to set item code in {row.drug_code}."
                    )
                )
            item = frappe.new_doc("Delivery Note Item")
            item.item_code = item_code
            item.item_name = item_name
            item.warehouse = warehouse
            item.is_restricted = row.is_restricted
            item.qty = row.quantity or 1
            item.medical_code = row.medical_code

            # TODO we have an amount on encounter, no need to fetch amount again
            if row.prescribe:
                item.rate = get_mop_amount(
                    item_code,
                    patient_encounter_doc.mode_of_payment,
                    patient_encounter_doc.company,
                    patient_encounter_doc.patient,
                )
                item.price_list_rate = item.rate
            else:
                item_rate = get_item_rate(
                    item_code,
                    patient_encounter_doc.company,
                    patient_encounter_doc.insurance_subscription,
                    patient_encounter_doc.insurance_company,
                )
                item.rate = item_rate - (item_rate * (discount_percent / 100))
                item.price_list_rate = item_rate
                if discount_percent > 0:
                    item.discount_percentage = discount_percent
                    item.hms_tz_is_discount_applied = 1

            item.reference_doctype = row.doctype
            item.reference_name = row.name
            item.description = ", <br>".join(
                [
                    "frequency: " + str(row.get("dosage") or "No Prescription Dosage"),
                    "period: " + str(row.get("period") or "No Prescription Period"),
                    "dosage_form: " + str(row.get("dosage_form") or ""),
                    "interval: " + str(row.get("interval") or ""),
                    "interval_uom: " + str(row.get("interval_uom") or ""),
                    "medical_code: "
                    + str(row.get("medical_code") or "No medical code"),
                    "Doctor's comment: "
                    + (row.get("comment") or "Take medication as per dosage."),
                ]
            )
            items.append(item)
            row.drug_prescription_created = 1
            row.db_update()
        if len(items) == 0:
            continue
        authorization_number = ""
        if (
            not patient_encounter_doc.insurance_subscription
            and patient_encounter_doc.inpatient_record
            or (
                patient_encounter_doc.mode_of_payment
                and patient_encounter_doc.healthcare_package_order
            )
        ):
            encounter_customer = frappe.get_cached_value(
                "Patient", patient_encounter_doc.patient, "customer"
            )
            insurance_coverage_plan = ""

        elif not encounter_customer:
            encounter_customer = frappe.get_cached_value(
                "Healthcare Insurance Company",
                patient_encounter_doc.insurance_company,
                "customer",
            )
            insurance_coverage_plan = patient_encounter_doc.insurance_coverage_plan
            authorization_number = frappe.get_value(
                "Patient Appointment",
                patient_encounter_doc.appointment,
                fieldname="authorization_number",
            )

        doc = frappe.get_doc(
            dict(
                doctype="Delivery Note",
                posting_date=nowdate(),
                posting_time=nowtime(),
                set_warehouse=element,
                company=patient_encounter_doc.company,
                customer=encounter_customer,
                currency=frappe.get_cached_value(
                    "Company", patient_encounter_doc.company, "default_currency"
                ),
                items=items,
                coverage_plan_name=insurance_coverage_plan,
                reference_doctype=patient_encounter_doc.doctype,
                reference_name=patient_encounter_doc.name,
                authorization_number=authorization_number,
                patient=patient_encounter_doc.patient,
                patient_name=patient_encounter_doc.patient_name,
                healthcare_service_unit=patient_encounter_doc.healthcare_service_unit,
                healthcare_practitioner=patient_encounter_doc.practitioner,
            )
        )
        doc.flags.ignore_permissions = True
        doc.set_missing_values()
        doc.insert(ignore_permissions=True)
        if doc.get("name"):
            # drug prescription will be updated only if delivery note is submitted
            # update_drug_prescription(patient_encounter_doc, doc.name)
            frappe.msgprint(
                _("Pharmacy Dispensing/Delivery Note {0} created successfully.").format(
                    frappe.bold(doc.name)
                )
            )


@frappe.whitelist()
def get_chronic_diagnosis(patient):
    data = frappe.get_all(
        "Codification Table",
        filters={
            "parent": patient,
            "parenttype": "Patient",
            "parentfield": "codification_table",
        },
        fields=["medical_code", "code", "description"],
    )
    return data


@frappe.whitelist()
def add_chronic_diagnosis(patient, encounter):
    patient_doc = frappe.get_doc("Patient", patient)
    encounter_doc = frappe.get_doc("Patient Encounter", encounter)

    prev_diagnos = len(patient_doc.codification_table)
    medical_codes = []
    if len(patient_doc.codification_table) == 0:
        for row in encounter_doc.patient_encounter_preliminary_diagnosis:
            patient_doc.append("codification_table", row)
        patient_doc.save(ignore_permissions=True)

    else:
        for d in patient_doc.codification_table:
            medical_codes.append(d.medical_code)
            for row in encounter_doc.patient_encounter_preliminary_diagnosis:
                if row.medical_code not in medical_codes:
                    patient_doc.append("codification_table", row)
        patient_doc.save(ignore_permissions=True)

    if len(patient_doc.codification_table) > prev_diagnos:
        frappe.msgprint("Chronic diagnosis added successfully")
    else:
        if prev_diagnos == 0:
            frappe.msgprint(
                "No chronic diagnosis added, <i>please save encounter and try again</i>"
            )
        else:
            frappe.msgprint("Chronic diagnosis already exist")


@frappe.whitelist()
def get_chronic_medications(patient):
    data = frappe.get_all(
        "Chronic Medications",
        filters={
            "parent": patient,
            "parenttype": "Patient",
            "parentfield": "chronic_medications",
        },
        fields=["*"],
    )
    return data


@frappe.whitelist()
def add_chronic_medications(patient, encounter, items):
    def clear_fields(drug_row):
        for field in [
            "name",
            "owner",
            "creation",
            "modified",
            "modified_by",
            "docstatus",
            "parent",
            "parentfield",
            "parenttype",
            "doctype",
            "idx",
        ]:
            if isinstance(drug_row, dict):
                row = frappe.parse_json(drug_row)
                if hasattr(row, field):
                    del row[field]
                drug_row = frappe._dict(row)
            elif isinstance(drug_row, object):
                row = drug_row.as_dict()
                if hasattr(row, field):
                    del row[field]
                drug_row = frappe._dict(row)
            else:
                raise ValueError("Unknown type for drug_row")

        return drug_row

    patient_doc = frappe.get_doc("Patient", patient)
    encounter_doc = frappe.get_doc("Patient Encounter", encounter)

    chronic_drug_items = []
    items = frappe.parse_json(items)
    if len(items) > 0:
        chronic_drug_items = items
    else:
        chronic_drug_items = encounter_doc.drug_prescription

    if len(chronic_drug_items) == 0:
        frappe.throw(_("No Chronic medications to add"))

    medications = []
    prev_chronic_medications = len(patient_doc.chronic_medications)
    if len(patient_doc.chronic_medications) == 0:
        for row in chronic_drug_items:
            new_row = clear_fields(row)
            patient_doc.append("chronic_medications", new_row)
        patient_doc.save(ignore_permissions=True)

    else:
        for d in patient_doc.chronic_medications:
            for row in chronic_drug_items:
                new_row = clear_fields(row)
                if d.drug_code == new_row.drug_code:
                    d.update(new_row)
                    medications.append(d.drug_code)
                    continue

        for d_row in chronic_drug_items:
            d_new_row = clear_fields(d_row)
            if d_new_row.drug_code not in medications:
                patient_doc.append("chronic_medications", d_new_row)
        patient_doc.save(ignore_permissions=True)

    if len(patient_doc.chronic_medications) > prev_chronic_medications:
        frappe.msgprint("Chronic medication added successfully")
    else:
        frappe.msgprint("Chronic medication already exist")


def validate_totals(doc, method):
    def get_field_map():
        childs_map = [
            {
                "table": "lab_test_prescription",
                "doctype": "Lab Test Template",
                "item": "lab_test_code",
            },
            {
                "table": "radiology_procedure_prescription",
                "doctype": "Radiology Examination Template",
                "item": "radiology_examination_template",
            },
            {
                "table": "procedure_prescription",
                "doctype": "Clinical Procedure Template",
                "item": "procedure",
            },
            {
                "table": "drug_prescription",
                "doctype": "Medication",
                "item": "drug_code",
            },
            {
                "table": "therapies",
                "doctype": "Therapy Type",
                "item": "therapy_type",
            },
        ]
        return childs_map

    def get_current_total(doc):
        doc.current_total = 0
        discount_percent = get_discount_percent(doc.insurance_company)

        for child in get_field_map():
            for row in doc.get(child.get("table")):
                if (
                    row.prescribe
                    or row.is_not_available_inhouse
                    or (row.is_cancelled and not row.hms_tz_is_limit_exceeded)
                ):
                    continue

                item_code = frappe.get_cached_value(
                    child.get("doctype"), row.get(child.get("item")), "item"
                )
                item_price_rate = get_item_rate(
                    item_code,
                    doc.company,
                    doc.insurance_subscription,
                    doc.insurance_company,
                )

                if hasattr(row, "quantity"):
                    quantity = row.quantity
                else:
                    quantity = 1

                item_rate = item_price_rate * quantity
                doc.current_total += item_rate - (item_rate * (discount_percent / 100))

    def mark_limit_exceeded(doc):
        for child in get_field_map():
            for row in doc.get(child.get("table")):
                if row.prescribe and row.hms_tz_is_limit_exceeded:
                    row.hms_tz_is_limit_exceeded = 0
                    row.is_cancelled = 0

                if (
                    row.prescribe
                    or row.is_not_available_inhouse
                    or (row.is_cancelled and not row.hms_tz_is_limit_exceeded)
                ):
                    continue

                if not row.hms_tz_is_limit_exceeded:
                    row.hms_tz_is_limit_exceeded = 1
                    row.is_cancelled = 1

    def unmark_limit_exceeded(doc):
        for child in get_field_map():
            for row in doc.get(child.get("table")):
                if row.hms_tz_is_limit_exceeded == 1:
                    row.hms_tz_is_limit_exceeded = 0
                    row.is_cancelled = 0

    if (
        not doc.insurance_company
        or not doc.insurance_subscription
        or "NHIF" in doc.insurance_company
        or not doc.daily_limit
        or doc.daily_limit == 0
        or doc.inpatient_record
        or doc.healthcare_package_order
    ):
        return

    if doc.encounter_type == "Initial":
        appointment_amount = frappe.get_value(
            "Patient Appointment", doc.appointment, "paid_amount"
        )
        doc.previous_total = appointment_amount

    get_current_total(doc)

    diff = doc.daily_limit - doc.current_total - doc.previous_total
    if diff < 0:
        diff = abs(diff)
        allow_submit_of_encounter_on_limit_exceed = frappe.get_cached_value(
            "Healthcare Insurance Coverage Plan",
            doc.insurance_coverage_plan,
            "hms_tz_submit_encounter_on_limit_exceed",
        )
        if allow_submit_of_encounter_on_limit_exceed == 0:
            msgThrow(
                _(
                    f"The total daily limit of <b>{doc.daily_limit}</b> for the Insurance Subscription <b>{doc.insurance_subscription}</b> has \
                    been exceeded by <b>{diff}</b>. <br> Please contact the reception to increase \
                    limit or prescribe the items"
                ),
                method=method,
            )
        else:
            mark_limit_exceeded(doc)
            msgPrint(
                _(
                    f"The total daily limit of <b>{doc.daily_limit}</b> for the Insurance Subscription <b>{doc.insurance_subscription}</b> has \
                        been exceeded by <b>{diff}</b>. <br> Please contact the reception to increase limit"
                ),
                method=method,
            )
    else:
        unmark_limit_exceeded(doc)


@frappe.whitelist()
def finalized_encounter(cur_encounter, ref_encounter=None):
    cur_encounter_doc = frappe.get_doc("Patient Encounter", cur_encounter)
    inpatient_status, inpatient_record = frappe.get_cached_value(
        "Patient", cur_encounter_doc.patient, ["inpatient_status", "inpatient_record"]
    )
    if inpatient_status and cur_encounter_doc.inpatient_record == inpatient_record:
        frappe.throw(
            _(
                "The patient {0} has inpatient status <strong>{1}</strong>. Please process the discharge before proceeding to finalize the encounter.".format(
                    cur_encounter_doc.patient, inpatient_status
                )
            )
        )

    frappe.set_value("Patient Encounter", cur_encounter, "encounter_type", "Final")

    if ref_encounter:
        encounters_list = frappe.get_all(
            "Patient Encounter",
            filters={"docstatus": 1, "reference_encounter": ref_encounter},
        )
        for element in encounters_list:
            frappe.set_value("Patient Encounter", element.name, "finalized", 1)
    else:
        frappe.set_value("Patient Encounter", cur_encounter, "finalized", 1)
        return


@frappe.whitelist()
def create_sales_invoice(encounter, encounter_category, encounter_mode_of_payment):
    encounter_doc = frappe.get_doc("Patient Encounter", encounter)
    encounter_category = frappe.get_doc("Encounter Category", encounter_category)
    if not encounter_category.create_sales_invoice:
        return

    doc = frappe.new_doc("Sales Invoice")
    doc.patient = encounter_doc.patient
    doc.customer = frappe.get_cached_value("Patient", encounter_doc.patient, "customer")
    doc.due_date = getdate()
    doc.company = encounter_doc.company
    doc.debit_to = get_receivable_account(encounter_doc.company)
    doc.healthcare_service_unit = encounter_doc.healthcare_service_unit
    doc.healthcare_practitioner = encounter_doc.practitioner

    item = doc.append("items", {})
    item.item_code = encounter_category.encounter_fee_item
    item.description = _("Consulting Charges: {0}").format(encounter_doc.practitioner)
    item.income_account = get_income_account(
        encounter_doc.practitioner, encounter_doc.company
    )
    item.cost_center = frappe.get_cached_value(
        "Company", encounter_doc.company, "cost_center"
    )
    item.qty = 1
    item.rate = encounter_category.encounter_fee
    item.reference_dt = "Patient Encounter"
    item.reference_dn = encounter_doc.name
    item.amount = encounter_category.encounter_fee

    doc.is_pos = 1
    payment = doc.append("payments", {})
    payment.mode_of_payment = encounter_mode_of_payment
    payment.amount = encounter_category.encounter_fee

    doc.set_taxes()
    doc.flags.ignore_permissions = True
    doc.set_missing_values(for_validate=True)
    doc.flags.ignore_mandatory = True
    doc.save(ignore_permissions=True)
    doc.calculate_taxes_and_totals()
    doc.submit()
    frappe.msgprint(_("Sales Invoice {0} created".format(doc.name)))
    encounter_doc.sales_invoice = doc.name
    encounter_doc.db_update()

    return "true"


def update_inpatient_record_consultancy(doc):
    if doc.inpatient_record:
        item_code = frappe.get_cached_value(
            "Healthcare Practitioner", doc.practitioner, "inpatient_visit_charge_item"
        )
        rate = 0

        # apply discount if it is available on Heathcare Insurance Company
        discount_percent = 0
        if doc.insurance_company and "NHIF" not in doc.insurance_company:
            discount_percent = get_discount_percent(doc.insurance_company)

        if doc.insurance_subscription:
            item_rate = get_item_rate(
                item_code,
                doc.company,
                doc.insurance_subscription,
                doc.insurance_company,
            )
            rate = item_rate - (item_rate * (discount_percent / 100))

        elif doc.mode_of_payment:
            price_list = frappe.get_cached_value(
                "Mode of Payment", doc.mode_of_payment, "price_list"
            )
            rate = get_item_price(item_code, price_list, doc.company)

        record_doc = frappe.get_doc("Inpatient Record", doc.inpatient_record)
        row = record_doc.append("inpatient_consultancy", {})
        row.date = nowdate()
        row.consultation_item = item_code
        row.rate = rate
        row.encounter = doc.name
        row.healthcare_practitioner = doc.practitioner
        if discount_percent > 0:
            row.hms_tz_is_discount_applied = 1

        record_doc.save(ignore_permissions=True)
        frappe.msgprint(
            _(f"Inpatient Consultancy record added for item {item_code}"),
            alert=True,
        )


def on_update_after_submit(doc, method):
    if doc.is_not_billable:
        return
    child_tables_list = [
        "lab_test_prescription",
        "radiology_procedure_prescription",
        "procedure_prescription",
        "drug_prescription",
    ]
    services_created_pending = 0
    for child_table_field in child_tables_list:
        if services_created_pending:
            break
        if doc.get(child_table_field):
            child_table = doc.get(child_table_field)
            for child in child_table:
                if child.doctype == "Lab Prescription":
                    if child.lab_test_created == 0:
                        services_created_pending = 1
                        break
                elif child.doctype == "Radiology Procedure Prescription":
                    if child.radiology_examination_created == 0:
                        services_created_pending = 1
                        break
                elif child.doctype == "Procedure Prescription":
                    if child.procedure_created == 0:
                        services_created_pending = 1
                        break
                elif child.doctype == "Drug Prescription":
                    if child.drug_prescription_created == 0:
                        services_created_pending = 1
                        break
    if services_created_pending == 0:
        doc.is_not_billable = 1
        # frappe.msgprint("done doc.is_not_billable = 1")
    else:
        doc.is_not_billable = 0
        # frappe.msgprint("done doc.is_not_billable = 0")
    if method == "enqueue":
        # frappe.msgprint("done method enqueue db commit")
        doc.db_update()


def enqueue_on_update_after_submit(doc_name):
    time.sleep(5)
    on_update_after_submit(frappe.get_doc("Patient Encounter", doc_name), "enqueue")


def before_submit(doc, method):
    if doc.insurance_company and "NHIF" in doc.insurance_company:
        validate_nhif_patient_claim_status(
            "Patient Encounter", doc.company, doc.appointment, doc.insurance_company
        )

    if not doc.healthcare_package_order:
        set_amounts(doc)

    # shm rock: 151
    set_practitioner_name(doc, method)

    if doc.inpatient_record:
        validate_patient_balance_vs_patient_costs(doc)

    encounter_create_sales_invoice = frappe.get_cached_value(
        "Encounter Category", doc.encounter_category, "create_sales_invoice"
    )
    if encounter_create_sales_invoice:
        if not doc.sales_invoice:
            frappe.throw(
                _(
                    "The encounter cannot be submitted as the Sales Invoice is not"
                    " created yet!<br><br>Click on Create Sales Invoice and Send to VFD"
                    " before submitting.",
                    "Cannot Submit Encounter",
                )
            )
        vfd_status = frappe.get_value("Sales Invoice", doc.sales_invoice, "vfd_status")
        if vfd_status == "Not Sent":
            frappe.throw(
                _(
                    "The encounter cannot be submitted as the Sales Invoice has not"
                    " been sent to VFD!<br><br>Click on Send to VFD before submitting.",
                    "Cannot Submit Encounter",
                )
            )


@frappe.whitelist()
def undo_finalized_encounter(cur_encounter, ref_encounter=None):
    encounters_list = frappe.get_all(
        "Patient Encounter",
        filters={"docstatus": 1, "reference_encounter": ref_encounter},
    )
    for element in encounters_list:
        frappe.set_value("Patient Encounter", element.name, "finalized", 0)
    if not ref_encounter:
        frappe.set_value("Patient Encounter", cur_encounter, "finalized", 0)
        return
    frappe.set_value("Patient Encounter", cur_encounter, "encounter_type", "Ongoing")


def set_amounts(doc):
    childs_map = [
        {
            "table": "lab_test_prescription",
            "doctype": "Lab Test Template",
            "item": "lab_test_code",
        },
        {
            "table": "radiology_procedure_prescription",
            "doctype": "Radiology Examination Template",
            "item": "radiology_examination_template",
        },
        {
            "table": "procedure_prescription",
            "doctype": "Clinical Procedure Template",
            "item": "procedure",
        },
        {
            "table": "drug_prescription",
            "doctype": "Medication",
            "item": "drug_code",
        },
        {
            "table": "therapies",
            "doctype": "Therapy Type",
            "item": "therapy_type",
        },
    ]

    # apply discount if it is available on Heathcare Insurance Company
    discount_percent = 0
    if doc.insurance_company and "NHIF" not in doc.insurance_company:
        discount_percent = get_discount_percent(doc.insurance_company)

    for child in childs_map:
        for row in doc.get(child.get("table")):
            if row.amount:
                continue

            item_rate = 0
            item_code = frappe.get_cached_value(
                child.get("doctype"), row.get(child.get("item")), "item"
            )
            if not item_code:
                frappe.throw(
                    _(
                        f"Item code for {row.get(child.get('item'))} set in row {row.idx} was not found.<br>Please set the item code in {child.get('doctype')}."
                    )
                )

            if row.prescribe and not doc.insurance_subscription:
                if doc.get("mode_of_payment"):
                    mode_of_payment = doc.get("mode_of_payment")
                elif doc.get("encounter_mode_of_payment"):
                    mode_of_payment = doc.get("encounter_mode_of_payment")
                item_rate = get_mop_amount(
                    item_code, mode_of_payment, doc.company, doc.patient
                )
                if not item_rate or item_rate == 0:
                    frappe.throw(
                        _(f"Cannot get rate for item {item_code} in {mode_of_payment}")
                    )

            elif row.prescribe and doc.insurance_subscription:
                price_list = frappe.get_cached_value(
                    "Company", doc.company, "default_price_list"
                )
                if not price_list:
                    frappe.throw(
                        _("Please set default price list in company {0}").format(
                            doc.company
                        )
                    )

                item_rate = get_item_price(item_code, price_list, doc.company)
                if not item_rate or item_rate == 0:
                    frappe.throw(
                        _("Cannot get mode of payment rate for item {0}").format(
                            item_code
                        )
                    )

            elif not row.prescribe:
                item_price_rate = get_item_rate(
                    item_code,
                    doc.company,
                    doc.insurance_subscription,
                    doc.insurance_company,
                )
                item_rate = item_price_rate - (
                    item_price_rate * (discount_percent / 100)
                )

                if discount_percent > 0:
                    row.hms_tz_is_discount_applied = 1
                    if row.doctype == "Drug Prescription":
                        row.hms_tz_is_discount_percent = discount_percent

            row.amount = item_rate


def inpatient_billing(patient_encounter_doc, method):
    if patient_encounter_doc.insurance_subscription:  # IPD/OPD insurance
        return
    if not patient_encounter_doc.inpatient_record:  # OPD cash or insurance
        return

    # SHM Rock: 207
    child_tables_list = [
        {
            "table_field": "lab_test_prescription",
            "item_field": "lab_test_code",
            "doctype": "Lab Test Template",
        },
        {
            "table_field": "radiology_procedure_prescription",
            "item_field": "radiology_examination_template",
            "doctype": "Radiology Examination Template",
        },
        {
            "table_field": "procedure_prescription",
            "item_field": "procedure",
            "doctype": "Clinical Procedure Template",
        },
        {
            "table_field": "drug_prescription",
            "item_field": "drug_code",
            "doctype": "Medication",
        },
        {
            "table_field": "therapies",
            "item_field": "therapy_type",
            "doctype": "Therapy Type",
        },
    ]
    for child_table_field in child_tables_list:
        if patient_encounter_doc.get(child_table_field.get("table_field")):
            child_table = patient_encounter_doc.get(
                child_table_field.get("table_field")
            )
            for child in child_table:
                is_disabled = frappe.get_cached_value(
                    child_table_field.get("doctype"),
                    child.get(child_table_field.get("item_field")),
                    "disabled",
                )
                if is_disabled == 1:
                    frappe.throw(
                        _(
                            f"{child_table_field.get('doctype')}: <b>{child.get(child_table_field.get('item_field'))}</b> selected at Row#: {child.idx} is <b>disabled</b>. Please select an enabled item."
                        )
                    )

                if (
                    child.is_cancelled
                    or child.is_not_available_inhouse
                    or child.hms_tz_is_limit_exceeded
                ):
                    continue
                if child.doctype == "Lab Prescription":
                    create_individual_lab_test(patient_encounter_doc, child)
                elif child.doctype == "Radiology Procedure Prescription":
                    create_individual_radiology_examination(
                        patient_encounter_doc, child
                    )
                elif child.doctype == "Procedure Prescription":
                    create_individual_procedure_prescription(
                        patient_encounter_doc, child
                    )
    create_delivery_note(patient_encounter_doc, method)


def show_last_prescribed(doc, method):
    if doc.is_new():
        return
    if method == "validate":
        msg = None
        valid_days_msg = ""
        for row in doc.drug_prescription:
            if row.is_cancelled or row.is_not_available_inhouse:
                continue

            item_code = frappe.get_cached_value("Medication", row.drug_code, "item")

            medication_list = frappe.db.sql(
                """
            select dn.posting_date, dni.item_code, dni.stock_qty, dni.uom from `tabDelivery Note` dn
            inner join `tabDelivery Note Item` dni on dni.parent = dn.name
                            where dni.item_code = %s
                            and dn.patient = %s
                            and dn.docstatus = 1
                            order by posting_date desc
                            limit 1"""
                % ("%s", "%s"),
                (item_code, doc.patient),
                as_dict=1,
            )
            if len(medication_list) > 0:
                msg = (
                    (msg or "")
                    + _(
                        "<strong>"
                        + row.drug_code
                        + "</strong>"
                        + " qty: <strong>"
                        + str(medication_list[0].get("stock_qty"))
                        + "</strong>, prescribed lastly on: <strong>"
                        + str(medication_list[0].get("posting_date"))
                    )
                    + "</strong><br>"
                )

                val_msg = validate_prescribe_days(
                    doc,
                    "Medication",
                    row.drug_code,
                    medication_list[0].get("posting_date"),
                )
                if val_msg:
                    valid_days_msg += val_msg

                # SHM Rock#: 169
                validate_medication_class(
                    doc.company, doc.name, doc.patient, row.drug_code
                )

        if valid_days_msg:
            frappe.msgprint(
                _(
                    "These Items should not be prescribed, because days are below minimum prescription days:<br>"
                    + valid_days_msg
                )
            )
        elif msg:
            frappe.msgprint(
                _(
                    "The below are the last related medication prescriptions:<br><br>"
                    + msg
                )
            )


def update_drug_prescription(patient_encounter_doc, name):
    dn_doc = frappe.get_doc("Delivery Note", name)

    for d in patient_encounter_doc.drug_prescription:
        if d.parent == dn_doc.reference_name:
            for item in dn_doc.items:
                if (d.name == item.reference_name) and (d.drug_code == item.item_code):
                    frappe.db.set_value(
                        "Drug Prescription", item.reference_name, "dn_detail", item.name
                    )


def validate_patient_balance_vs_patient_costs(doc, encounters=None):
    if not encounters or len(encounters) == 0:
        encounters = get_patient_encounters(doc)

        if not encounters or len(encounters) == 0:
            return

    total_amount_billed = 0

    child_map = [
        {"child_table": "lab_test_prescription"},
        {"child_table": "radiology_procedure_prescription"},
        {"child_table": "procedure_prescription"},
        {"child_table": "drug_prescription"},
        {"child_table": "therapies"},
    ]
    for enc in encounters:
        encounter_doc = frappe.get_doc("Patient Encounter", enc)

        for row in child_map:
            for child in encounter_doc.get(row.get("child_table")):
                if (
                    child.prescribe == 0
                    or child.is_not_available_inhouse == 1
                    or child.invoiced == 1
                    or child.is_cancelled == 1
                ):
                    continue

                if child.doctype == "Drug Prescription":
                    total_amount_billed += (
                        child.quantity - child.quantity_returned
                    ) * child.amount
                else:
                    total_amount_billed += child.amount

    inpatient_record_doc = frappe.get_doc("Inpatient Record", doc.inpatient_record)

    cash_limit = inpatient_record_doc.cash_limit

    for record in inpatient_record_doc.inpatient_occupancies:
        if not record.is_confirmed:
            continue

        total_amount_billed += record.amount

    for record in inpatient_record_doc.inpatient_consultancy:
        if not record.is_confirmed:
            continue

        total_amount_billed += record.rate

    # get balance from payment entry after patient has deposit advances
    deposit_balance = get_balance_on(
        party_type="Customer", party=doc.patient_name, company=doc.company
    )

    patient_balance = (-1 * deposit_balance) + cash_limit

    cash_limit_percent = 100 - ((total_amount_billed / patient_balance) * 100)
    cash_limit_details = frappe.get_value(
        "Company",
        {"name": doc.company, "hms_tz_has_cash_limit_alert": 1},
        [
            "hms_tz_minimum_cash_limit_percent",
            "hms_tz_limit_exceed_action",
            "hms_tz_limit_under_minimum_percent_action",
        ],
        as_dict=1,
    )

    make_cash_limit_alert(doc, cash_limit_percent, cash_limit_details)


def make_cash_limit_alert(doc, cash_limit_percent, cash_limit_details):
    if cash_limit_percent > 0 and cash_limit_percent <= cash_limit_details.get(
        "hms_tz_minimum_cash_limit_percent"
    ):
        msg_per = f"""<div style="border: 1px solid #ccc; background-color: #f9f9f9; padding: 10px; border-radius: 5px; box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1); margin: 10px;">
                <p style="font-weight: normal; font-size: 14px; justify-content: left;">The patient: <span style="font-weight: bold;">{doc.patient}</span> - <span style="font-weight: bold;">{doc.patient_name}</span>\
                    has reached <span style="font-weight: bold;">{100 - flt(cash_limit_percent, 2)}%</span> of his/her cash limit.</p>
                <p style="font-style: italic; font-weight: bold; font-size: 14px; justify-content: left;">please request patient to deposit advances or request patient cash limit adjustment</p>
            </div>"""

        if (
            cash_limit_details.get("hms_tz_limit_under_minimum_percent_action")
            == "Warn"
        ):
            frappe.msgprint(
                title="Cash Limit Exceeded",
                msg=msg_per,
            )

        elif (
            cash_limit_details.get("hms_tz_limit_under_minimum_percent_action")
            == "Stop"
        ):
            frappe.throw(
                title="Cash Limit Exceeded",
                msg=msg_per,
            )

    elif cash_limit_percent <= 0:
        msg = f"""<div style="border: 1px solid #ccc; background-color: #f9f9f9; padding: 10px; border-radius: 5px; box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1); margin: 10px;">
                <p style="font-weight: normal; font-size: 14px; justify-content: left;">The deposit balance of this patient: <span style="font-weight: bold;">{doc.patient}</span> - <span style="font-weight: bold;">{doc.patient_name}</span>\
                    is not enough or Patient has reached the cash limit.</p>
                <p style="font-style: italic; font-weight: bold; font-size: 14px; justify-content: left;">please request patient to deposit advances or request patient cash limit adjustment</p>
            </div>"""

        if cash_limit_details.get("hms_tz_limit_exceed_action") == "Warn":
            frappe.msgprint(
                title="Cash Limit Exceeded",
                msg=msg,
            )

        if cash_limit_details.get("hms_tz_limit_exceed_action") == "Stop":
            frappe.throw(
                title="Cash Limit Exceeded",
                msg=msg,
            )


def get_patient_encounters(doc):
    if doc.mode_of_payment != "" and doc.inpatient_record != "":
        patient_encounters = frappe.get_all(
            "Patient Encounter",
            filters={
                "patient": doc.patient,
                "appointment": doc.appointment,
                "inpatient_record": doc.inpatient_record,
            },
            fields=["name"],
            pluck="name",
        )
        return patient_encounters


def show_last_prescribed_for_lrpt(doc, method):
    childs_map = [
        {
            "table": "lab_test_prescription",
            "doctype": "Lab Test Template",
            "item": "lab_test_code",
            "ref_doc": "Lab Test",
            "field_name": "template",
        },
        {
            "table": "radiology_procedure_prescription",
            "doctype": "Radiology Examination Template",
            "item": "radiology_examination_template",
            "ref_doc": "Radiology Examination",
            "field_name": "radiology_examination_template",
        },
        {
            "table": "procedure_prescription",
            "doctype": "Clinical Procedure Template",
            "item": "procedure",
            "ref_doc": "Clinical Procedure",
            "field_name": "procedure_template",
        },
        # {
        # "table": "therapies",
        # "doctype": "Therapy Type",
        # "item": "therapy_type",
        # "ref_doc": "Therapy Plan",
        # "field_name": "therapy_plan_template"
        # }
    ]

    if method == "validate":
        msg = ""
        valid_days_msg = ""
        for child in childs_map:
            msg_print = ""
            for entry in doc.get(child.get("table")):
                conditions = {
                    "patient": doc.patient,
                    child.get("field_name"): entry.get(child.get("item")),
                }

                item_doc = frappe.get_all(
                    child.get("ref_doc"),
                    filters=conditions,
                    fields=[child.get("field_name"), "creation"],
                    order_by="creation DESC",
                    limit=1,
                )

                if len(item_doc) > 0:
                    date = item_doc[0]["creation"].strftime("%Y-%m-%d")

                    msg_print += _(
                        "{0} prescribed last on: {1}".format(
                            frappe.bold(entry.get(child.get("item"))), frappe.bold(date)
                        )
                        + "<br>"
                    )

                    val_msg = validate_prescribe_days(
                        doc, child.get("doctype"), entry.get(child.get("item")), date
                    )
                    if val_msg:
                        valid_days_msg += val_msg

            msg += msg_print

        for plan in doc.therapies:
            items = frappe.db.sql(
                """ 
                SELECT tpd.therapy_type, Date(tpd.creation) AS date FROM `tabTherapy Plan Detail` tpd
                INNER JOIN `tabTherapy Plan` tp ON tpd.parent = tp.name WHERE tp.patient = %s 
                AND tpd.therapy_type = %s """
                % (frappe.db.escape(doc.patient), frappe.db.escape(plan.therapy_type)),
                as_dict=1,
            )

            if items:
                msg = _(
                    msg
                    + "{0} prescribed last on: {1}".format(
                        frappe.bold(items[0]["therapy_type"]),
                        frappe.bold(items[0]["date"]),
                    )
                    + "<br>"
                )
                val_msg = validate_prescribe_days(
                    doc, "Therapy Type", items[0]["therapy_type"], items[0]["date"]
                )
                if val_msg:
                    valid_days_msg += val_msg

        if valid_days_msg:
            frappe.throw(
                _(
                    "These Items should not be prescribed, since days are below minimum prescription days:<br>"
                    + valid_days_msg
                ),
            )
        elif msg:
            frappe.msgprint(
                _("The below are the last related Item prescribed:<br><br>" + msg)
            )


def validate_prescribe_days(doc, doctype, item_value, date):
    valid_min_presribe_days = None
    if doc.insurance_company:
        valid_min_presribe_days = frappe.get_value(
            doctype,
            {"name": item_value, "hms_tz_validate_prescription_days_for_insurance": 1},
            "hms_tz_insurance_min_no_of_days_for_prescription",
        )

    elif doc.mode_of_payment:
        valid_min_presribe_days = frappe.get_value(
            doctype,
            {"name": item_value, "hms_tz_validate_prescription_days_for_cash": 1},
            "hms_tz_cash_min_no_of_days_for_prescription",
        )

    if valid_min_presribe_days and (
        date_diff(nowdate(), date) < cint(valid_min_presribe_days)
    ):
        item = item_value
        msg = _(
            f"<p style='background-color: #CCFB5D;'><b>{item}</b> was lastly prescribed on: <b>{date}</b> and it should be prescribed again after: <b>{valid_min_presribe_days} days</b></p><br>"
        )

        return msg


@frappe.whitelist()
def convert_opd_encounter_to_ipd_encounter(encounter):
    """Convert an out-patient encounter into list of inpatient encounters.

    This can be used when items for opd encounters needs to be created with inpatient
    functionality of create pending healthcare services while the encounter
    does not have inpatient record

    :param of encounter: name of the encounter to be converted to inpatient encounter
    """

    doc = frappe.get_doc("Patient Encounter", encounter)
    if doc.inpatient_record:
        frappe.msgprint(
            "<p class='text-center font-weight-bold h6' style='background-color: #DCDCDC; font-size: 12pt;'>\
                This encounter having inpatient record: {0} already".format(
                frappe.bold(doc.inpatient_record)
            )
            + "</p>"
        )
        return

    inpatient_record, inpatient_status = frappe.get_cached_value(
        "Patient", doc.patient, ["inpatient_record", "inpatient_status"]
    )
    if not inpatient_record:
        inpatient_details_from_encounters = frappe.get_all(
            "Patient Encounter",
            filters={"appointment": doc.appointment, "inpatient_record": ["!=", ""]},
            fields=["inpatient_record", "inpatient_status"],
            page_length=1,
        )
        if inpatient_details_from_encounters:
            inpatient_record = inpatient_details_from_encounters[0].inpatient_record
            inpatient_status = inpatient_details_from_encounters[0].inpatient_status

        if not inpatient_record:
            frappe.throw(
                "<p class='text-center font-weight-bold h6' style='background-color: #DCDCDC; font-size: 11pt;'>\
                    Scheduling admission was not done for this patient: {0} of appointment: {1}.".format(
                    frappe.bold(doc.patient), frappe.bold(doc.appointment)
                )
                + "</p>"
            )

    doc.inpatient_record = inpatient_record
    doc.inpatient_status = inpatient_status
    doc.save(ignore_permissions=True)

    if doc.get("inpatient_record"):
        create_healthcare_docs_from_name(doc.name)

        frappe.msgprint(
            "<p class='text-center font-weight-bold h6' style='background-color: #DCDCDC; font-size: 11pt;'>\
            This encounter is now having inpatient record: {0}".format(
                frappe.bold(doc.get("inpatient_record"))
            )
            + "</p>"
        )
        doc.reload()
        return True


@frappe.whitelist()
def validate_admission_encounter(encounter, healthcare_package_order=None):
    """Validate encounter if it has duplicated = 1 and if it has healthcare package order"""

    if healthcare_package_order:
        frappe.msgprint(
            f"This encounter has healhcare package order: <b>{healthcare_package_order}</b>,<br>you can't schedule Admission on it"
        )
        return True

    duplicated_encounter = frappe.get_value(
        "Patient Encounter", {"from_encounter": encounter}, "name"
    )
    if duplicated_encounter:
        url = frappe.utils.get_link_to_form("Patient Encounter", duplicated_encounter)
        frappe.msgprint(
            "You can't schedule Admission on this encounter: {0},<br>\
            Please, Click Here: {1} to open the right encounter".format(
                frappe.bold(encounter), frappe.bold(url)
            )
        )
        return True


@frappe.whitelist()
def get_previous_diagnosis_and_lrpmt_items_to_reuse(kwargs, caller):
    """Get unique Diagnosis and LRPMT items from previous encounters that can be reused on current encounters"""

    kwargs = frappe.parse_json(kwargs)
    if not kwargs.get("patient"):
        return []

    appointments = frappe.get_all(
        "Patient Appointment",
        filters={
            "patient": kwargs.get("patient"),
            "name": ["!=", kwargs.get("appointment")],
            "status": "Closed",
        },
        fields=["name"],
        limit_page_length=kwargs.get("number_of_visit"),
        order_by="appointment_date desc",
        pluck="name",
    )
    if not appointments:
        return []

    enc_cond = {"appointment": ["in", appointments]}
    if not kwargs.get("include_ipd_encounters"):
        enc_cond["inpatient_record"] = ("=", "")

    encounters = frappe.get_all(
        "Patient Encounter", filters=enc_cond, fields=["name"], pluck="name"
    )
    if not encounters:
        return []

    data = []
    if caller == "Diagnosis":
        diagnosis = frappe.get_all(
            kwargs.doctype,
            fields=kwargs.get("fields"),
            filters={
                "parent": ["in", encounters],
                "parentfield": "patient_encounter_final_diagnosis",
            },
            order_by="creation desc",
        )
        data = list({v["item"]: v for v in diagnosis}.values())
    else:
        items = frappe.get_all(
            kwargs.doctype,
            fields=kwargs.get("fields"),
            filters={
                "parent": ["in", encounters],
                "is_cancelled": 0,
                "is_not_available_inhouse": 0,
            },
            order_by="creation desc",
        )
        unique_items = []
        for item in items:
            if item.item not in unique_items:
                unique_items.append(item.item)
                data.append(item)

    return data


@frappe.whitelist()
def get_encounter_cost_estimate(encounter_doc):
    """Get encounter cost estimate"""
    if not encounter_doc:
        return

    childs_map = [
        {
            "table": "lab_test_prescription",
            "lable": "Lab Test",
            "item": "lab_test_code",
        },
        {
            "table": "radiology_procedure_prescription",
            "lable": "Radiology Examination",
            "item": "radiology_examination_template",
        },
        {
            "table": "procedure_prescription",
            "lable": "Clinical Procedure",
            "item": "procedure",
        },
        {
            "table": "drug_prescription",
            "lable": "Medication",
            "item": "drug_code",
        },
        {
            "table": "therapies",
            "lable": "Therapy Type",
            "item": "therapy_type",
        },
    ]

    encounter_doc = frappe.get_doc(json.loads(encounter_doc))
    # set encounter amounts
    set_amounts(encounter_doc)
    # get encounter cost estimate details
    cost_dict = {}
    for child_table_dict in childs_map:
        child_table = child_table_dict.get("table")
        if not encounter_doc.get(child_table):
            continue
        cost_dict.setdefault(child_table_dict["lable"], [])

        for row in encounter_doc.get(child_table):
            cost_row = {}
            quantity = 1
            if hasattr(row, "quantity"):
                quantity = row.quantity

            cost_row["item"] = row.get(child_table_dict.get("item"))
            cost_row["amount"] = row.amount * quantity

            cost_dict[child_table_dict["lable"]].append(cost_row)

    total_cost = 0
    # calculate total cost
    for key, value in cost_dict.items():
        for row in value:
            total_cost += row.get("amount") or 0

    return {"total_cost": total_cost, "details": cost_dict}


@frappe.whitelist()
def get_drug_quantity(drug_item):
    """Get drug quantity based on dosage, period, interval and interval uom

    :param drug_item: object or json string of drug item
    """
    if not frappe.db.get_single_value(
        "Healthcare Settings", "enable_auto_quantity_calculation"
    ):
        return 0

    quantity = 0
    strength_count = 0

    drug_row = frappe.parse_json(drug_item)

    if drug_row.dosage and drug_row.period:
        dosage = frappe.get_doc("Prescription Dosage", drug_row.dosage)
        period = frappe.get_doc("Prescription Duration", drug_row.period)
        for item in dosage.dosage_strength:
            strength_count += item.strength
        if strength_count == 0:
            strength_count = dosage.default_strength
        if strength_count > 0:
            if drug_row.interval and drug_row.interval_uom:
                if drug_row.interval_uom == "Day" and drug_row.interval:
                    quantity = strength_count * (period.get_days() / drug_row.interval)
                elif drug_row.interval_uom == "Hour" and drug_row.interval:
                    quantity = strength_count * (period.get_hours() / drug_row.interval)
            else:
                quantity = strength_count * period.get_days()

        # elif drug_row.interval and drug_row.interval_uom:
        #     if drug_row.interval_uom == "Day" and drug_row.interval:
        #         quantity = period.get_days() / drug_row.interval
        #     elif drug_row.interval_uom == "Hour" and drug_row.interval:
        #         quantity = period.get_hours() / drug_row.interval

    if quantity > 0:
        return quantity
    else:
        return 1


@frappe.whitelist()
def validate_medication_class(company, encounter, patient, drug_item, caller="Backend"):
    """Validate medication class based on company settings

    Args:
        company (str): company name
        encounter (str): patient encounter id
        patient (str): patient id
        drug_item (str): drug item name
        caller (str, optional): excute location. Defaults to "Backend".
    """

    validate_medication_class = frappe.get_cached_value(
        "Company", company, "validate_medication_class"
    )
    if int(validate_medication_class) == 0:
        return

    medication_class = frappe.get_cached_value(
        "Medication", drug_item, "medication_class"
    )
    if not medication_class:
        return

    medication_class_list = frappe.db.sql(
        f"""
        SELECT dp.drug_code, pe.name, pe.encounter_date, mc.prescribed_after as valid_days
        FROM `tabDrug Prescription` dp
        INNER JOIN `tabMedication` m ON m.name = dp.drug_code
        INNER JOIN `tabMedication Class` mc ON mc.name = m.medication_class
        INNER JOIN `tabPatient Encounter` pe ON pe.name = dp.parent
        WHERE dp.is_cancelled = 0 
            AND dp.is_not_available_inhouse = 0
            AND dp.dn_detail != ""
            AND dp.parent != {frappe.db.escape(encounter)}
            AND mc.name = {frappe.db.escape(medication_class)}
            AND pe.docstatus = 1
            AND pe.patient = {frappe.db.escape(patient)}
        order by pe.encounter_date Desc
    """,
        as_dict=1,
    )

    if len(medication_class_list) == 0:
        return

    prescribed_date = medication_class_list[0].encounter_date
    drug_code = medication_class_list[0].drug_code
    valid_days = medication_class_list[0].valid_days
    if not int(valid_days):
        return

    if int(date_diff(nowdate(), prescribed_date)) < int(valid_days):
        if caller == "Front End":
            return {
                "prescribed_date": prescribed_date,
                "drug_item": drug_code,
                "valid_days": valid_days,
                "medication_class": medication_class,
            }

        frappe.msgprint(
            _(
                f"Item: <strong>{drug_code}</strong> with same Medication Class: <strong>{medication_class}</strong> was lastly prescribed on: <strong>{prescribed_date}</strong><br>\
            Therefore item with same <b>medication class</b> were supposed to be prescribed after: <strong>{valid_days}</strong> days"
            )
        )


def set_practitioner_name(doc, method):
    submitting_healthcare_practitioner = frappe.db.get_value(
        "Healthcare Practitioner",
        {"user_id": frappe.session.user, "hms_tz_company": doc.company},
        ["name", "practitioner_name"],
        as_dict=1,
    )

    if submitting_healthcare_practitioner:
        doc.practitioner = submitting_healthcare_practitioner.name
        doc.practitioner_name = submitting_healthcare_practitioner.practitioner_name

    elif (
        doc.encounter_category == "Appointment"
        and not doc.healthcare_package_order
        and doc.practitioner not in ["Direct Cash", "Direct Insurance"]
    ):
        if method not in ("before_insert", "validate"):
            frappe.throw(
                _(
                    f"Please set user id: <b>{frappe.session.user}</b>\
                in Healthcare Practitioner<br>\
                so as to set the correct practitioner, who submitting this encounter"
                )
            )


def validate_medical_code(doc, method):
    """
    Validate medical code on patient encounter based on the configuration

    for cash patients its configuration is on Healthcare Settings
    for insurance patients its configuration is on Healthcare Insurance Company
    """

    validation_for_medical_code = None
    if doc.insurance_subscription:
        validation_for_medical_code = frappe.db.get_value(
            "Healthcare Insurance Company",
            doc.insurance_company,
            "validate_medical_code_for_insurance_patients",
        )
    else:
        validation_for_medical_code = frappe.db.get_single_value(
            "Healthcare Settings", "validate_medical_code_for_cash_patients"
        )

    if validation_for_medical_code == 0:
        return

    def medical_code_mapping():
        return {
            "patient_encounter_preliminary_diagnosis": [
                "lab_test_prescription",
                "radiology_procedure_prescription",
            ],
            "patient_encounter_final_diagnosis": [
                "procedure_prescription",
                "drug_prescription",
                "therapies",
                "diet_recommendation",
            ],
        }

    def get_diagnosis_list(doc, diagnosis_table):
        diagnosis_list = []
        if doc.get(diagnosis_table):
            for row in doc.get(diagnosis_table):
                if not row.medical_code:
                    continue
                d = str(row.medical_code) + "\n " + str(row.description)
                diagnosis_list.append(d)
        return diagnosis_list

    for from_table, fields in medical_code_mapping().items():
        diagnosis_list = get_diagnosis_list(doc, from_table)

        from_table_label = frappe.get_meta(doc.doctype).get_label(from_table)
        for fieldname in fields:
            if not doc.get(fieldname):
                continue

            fieldname_label = frappe.get_meta(doc.doctype).get_label(fieldname)
            for row in doc.get(fieldname):
                if row.medical_code not in diagnosis_list:
                    msgThrow(
                        _(
                            f"The Medical Code in the <strong>{fieldname_label}</strong> table at line <strong>{row.idx}</strong> is empty\
                            or does not exist in the <strong>{from_table_label}</strong> table."
                        ),
                        method,
                    )


def create_items_from_healthcare_package_orders(doc, method):
    child_tables_list = [
        "lab_test_prescription",
        "radiology_procedure_prescription",
        "procedure_prescription",
    ]
    for child_table_field in child_tables_list:
        if doc.get(child_table_field):
            child_table = doc.get(child_table_field)
            for child in child_table:
                if child.is_cancelled or child.hms_tz_is_limit_exceeded:
                    continue
                if child.doctype == "Lab Prescription":
                    create_individual_lab_test(doc, child)
                elif child.doctype == "Radiology Procedure Prescription":
                    create_individual_radiology_examination(doc, child)
                elif child.doctype == "Procedure Prescription":
                    create_individual_procedure_prescription(doc, child)
    create_delivery_note(doc, method)


@frappe.whitelist()
def get_filterd_drug(doctype, txt, searchfield, start, page_len, filters):
    """
    Get filtered drug based on the search criteria
    and retrun Mediction if it is not disabled and allowed price list is set
    """
    conditions = "MD.disabled = 0"
    if txt:
        conditions += f" AND MD.name LIKE '%{txt}%'"
    if filters.get("price_list"):
        conditions += f" AND APL.price_list = '{filters.get('price_list')}'"

    data = frappe.db.sql(
        f"""
        SELECT
            MD.name, MD.national_drug_code, MD.generic_name, MD.strength_text
        FROM
            `tabMedication` MD
        inner join
            `tabAllowed Price List` APL
        on
            MD.name = APL.parent
        WHERE
              {conditions}
        ORDER BY
            name ASC
        LIMIT
            {start}, {page_len}
    """
    )

    return data


@frappe.whitelist()
def get_filtered_dosage(doctype, txt, searchfield, start, page_len, filters):
    doctype = "Prescription Dosage"
    if filters.get("dosage_form"):
        if (
            frappe.get_cached_value(
                "Dosage Form", filters.get("dosage_form"), "has_restricted_qty"
            )
            == 1
        ):
            return frappe.get_all(
                doctype,
                filters={"has_restricted_qty": 1},
                fields=[searchfield],
                as_list=1,
            )
        else:
            return frappe.get_all(
                "Prescription Dosage",
                fields=[searchfield],
                as_list=1,
            )
    else:
        return frappe.get_all(
            "Prescription Dosage",
            fields=[searchfield],
            as_list=1,
        )
