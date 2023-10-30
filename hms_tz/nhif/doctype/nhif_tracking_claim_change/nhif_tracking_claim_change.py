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
    ref_docnames_list = []

    for row in claim.original_nhif_patient_claim_item:
        for item in claim.nhif_patient_claim_item:
            if item.item_code == row.item_code:
                if item.amount_claimed == row.amount_claimed:
                    ref_docnames_list.append(item.ref_docname)

                elif item.amount_claimed != row.amount_claimed:
                    ref_docnames_list.append(item.ref_docname)
                    create_nhif_track_record(
                        item, claim, row.amount_claimed, "Amount Changed"
                    )

        if row.ref_docname not in ref_docnames_list:
            if row.ref_doctype == "Patient Appointment":
                create_nhif_track_record(row, claim, row.amount_claimed, "Item Removed")

            elif row.ref_doctype == "Drug Prescription":
                handle_drug_prescription_changes(row, claim)

            elif row.ref_doctype in [
                "Lab Prescription",
                "Radiology Procedure Prescription",
                "Procedure Prescription",
                "Therapy Plan Detail",
            ]:
                handle_lrpt_prescription_changes(row, claim)

            elif row.ref_doctype in ["Inpatient Consultancy", "Inpatient Occupancy"]:
                handle_inpatient_changes(row, claim)


def create_nhif_track_record(
    item, claim_doc, prev_amount, status, lrpmt_return=None, med_change_request=None
):
    amount_changed = abs(prev_amount - item.amount_claimed)
    new_item = frappe.get_doc(
        {
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
            "ref_doctype": item.ref_doctype,
            "patient_encounter": item.patient_encounter,
            "lrpmt_return": lrpmt_return,
            "medication_change_request": med_change_request,
            "user_email": frappe.session.user,
            "edited_by": get_fullname(),
        }
    ).insert(ignore_permissions=True)


def handle_drug_prescription_changes(item, claim_doc):
    def handle_drug_changes(
        item, ref_docname, is_cancelled, child_encounter, claim_row_encounter
    ):
        if not is_cancelled and not child_encounter:
            med_change_request = get_medication_change_request_reference(
                item.item_name, claim_row_encounter
            )
            if med_change_request:
                create_nhif_track_record(
                    item,
                    claim_doc,
                    item.amount_claimed,
                    "Item Replaced",
                    med_change_request=med_change_request,
                )

        elif child_encounter and is_cancelled == 0:
            create_nhif_track_record(
                item, claim_doc, item.amount_claimed, "Item Removed"
            )

        elif child_encounter and is_cancelled == 1:
            lrpmt_return = frappe.db.get_value(
                "Medication Return",
                {
                    "parentfield": "drug_items",
                    "parenttype": "LRPMT Returns",
                    "child_name": ref_docname,
                    "encounter_no": child_encounter,
                },
                "parent",
            )
            if lrpmt_return:
                create_nhif_track_record(
                    item,
                    claim_doc,
                    item.amount_claimed,
                    "Item Cancelled",
                    lrpmt_return=lrpmt_return,
                )

    if "," not in item.ref_docname:
        is_cancelled = None
        child_encounter = None
        try:
            is_cancelled, child_encounter = frappe.db.get_value(
				item.ref_doctype, item.ref_docname, ["is_cancelled", "parent as encounter"]
			)
        except TypeError as e:
            pass
            
        handle_drug_changes(
            item,
            item.ref_docname,
            is_cancelled,
            child_encounter,
            item.patient_encounter,
        )

    elif "," in item.ref_docname:
        for ref_name in item.ref_docname.split(","):
            is_cancelled = None
            child_encounter = None
            try:
                is_cancelled, child_encounter = frappe.db.get_value(
					item.ref_doctype, ref_name, ["is_cancelled", "parent as encounter"]
				)
            except TypeError as e:
                pass

            handle_drug_changes(
                item,
                ref_name,
                is_cancelled,
                child_encounter,
                item.patient_encounter
            )


def handle_lrpt_prescription_changes(item, claim_doc):
    def handle_lrpt_changes(item, ref_docname, is_cancelled, child_encounter):
        if child_encounter and is_cancelled == 0:
            create_nhif_track_record(
                item, claim_doc, item.amount_claimed, "Item Removed"
            )

        elif child_encounter and is_cancelled == 1:
            lrpmt_return = frappe.db.get_value(
                "Item Return",
                {
                    "parentfield": "lrpt_items",
                    "parenttype": "LRPMT Returns",
                    "child_name": ref_docname,
                    "encounter_no": child_encounter,
                },
                "parent",
            )
            if lrpmt_return:
                create_nhif_track_record(
                    item,
                    claim_doc,
                    item.amount_claimed,
                    "Item Cancelled",
                    lrpmt_return=lrpmt_return,
                )

    if "," not in item.ref_docname:
        is_cancelled, child_encounter = frappe.db.get_value(
            item.ref_doctype, item.ref_docname, ["is_cancelled", "parent as encounter"]
        )
        handle_lrpt_changes(item, item.ref_docname, is_cancelled, child_encounter)

    elif "," in item.ref_docname:
        for ref_name in item.ref_docname.split(","):
            is_cancelled, child_encounter = frappe.db.get_value(
                item.ref_doctype, ref_name, ["is_cancelled", "parent as encounter"]
            )
            handle_lrpt_changes(item, ref_name, is_cancelled, child_encounter)


def handle_inpatient_changes(item, claim_doc):
    def handle_beds_cons_changes(item, ref_docname, is_confirmed):
        if is_confirmed == 0:
            create_nhif_track_record(
                item, claim_doc, item.amount_claimed, "Item Unconfirmed"
            )
        else:
            create_nhif_track_record(
                item, claim_doc, item.amount_claimed, "Item Removed"
            )

    if "," not in item.ref_docname:
        is_confirmed = frappe.db.get_value(
            item.ref_doctype, item.ref_docname, ["is_confirmed"]
        )
        handle_beds_cons_changes(item, item.ref_docname, is_confirmed)

    elif "," in item.ref_docname:
        for ref_name in item.ref_docname.split(","):
            is_confirmed = frappe.db.get_value(
                item.ref_doctype, ref_name, ["is_confirmed"]
            )
            handle_beds_cons_changes(item, ref_name, is_confirmed)


def get_medication_change_request_reference(item, encounter):
    dp = frappe.qb.DocType("Drug Prescription")
    md = frappe.qb.DocType("Medication Change Request")

    ref_name = (
        frappe.qb.from_(md)
        .inner_join(dp)
        .on(md.name == dp.parent)
        .select(md.name)
        .where(
            (dp.drug_name == item)
            & (md.patient_encounter == encounter)
            & (dp.parenttype == "Medication Change Request")
            & (dp.parentfield == "original_pharmacy_prescription")
        )
    ).run(as_dict=1)

    return ref_name[0].name if ref_name else None
