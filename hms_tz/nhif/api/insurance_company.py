# get_nhif_price_package

from __future__ import unicode_literals
import frappe
from frappe import _
from hms_tz.nhif.api.token import get_claimsservice_token
import json
import requests
from frappe.utils.background_jobs import enqueue
from hms_tz.nhif.doctype.nhif_product.nhif_product import add_product
from hms_tz.nhif.doctype.nhif_scheme.nhif_scheme import add_scheme
from frappe.utils import now
from hms_tz.nhif.doctype.nhif_response_log.nhif_response_log import add_log
from frappe.model.naming import set_new_name


@frappe.whitelist()
def enqueue_get_nhif_price_package(company):
    enqueue(method=get_nhif_price_package, queue='long',
            timeout=10000000, is_async=True, kwargs=company)
    frappe.msgprint(_("Start Getting NHIF Prices Packages"), alert=True)
    return


def get_nhif_price_package(kwargs):
    company = kwargs
    user = frappe.session.user
    frappe.db.sql("DELETE FROM `tabNHIF Price Package` WHERE name != 'ABC'")
    frappe.db.sql(
        "DELETE FROM `tabNHIF Excluded Services` WHERE name != 'ABC'")
    frappe.db.commit()
    token = get_claimsservice_token(company)
    claimsserver_url, facility_code = frappe.get_value(
        "Company NHIF Settings", company, ["claimsserver_url", "facility_code"])
    headers = {
        "Authorization": "Bearer " + token
    }
    url = str(claimsserver_url) + \
        "/claimsserver/api/v1/Packages/GetPricePackageWithExcludedServices?FacilityCode=" + \
        str(facility_code)
    r = requests.get(url, headers=headers, timeout=5)
    if r.status_code != 200:
        add_log(
            request_type="GetCardDetails",
            request_url=url,
            request_header=headers,
        )
        frappe.throw(json.loads(r.text))
    else:
        if json.loads(r.text):
            log_name = add_log(
                request_type="GetPricePackageWithExcludedServices",
                request_url=url,
                request_header=headers,
                response_data=json.loads(r.text)
            )
            time_stamp = now()
            data = json.loads(r.text)
            insert_data = []
            for item in data.get("PricePackage"):
                insert_data.append((
                    frappe.generate_hash("", 20),
                    facility_code,
                    time_stamp,
                    log_name,
                    item.get("ItemCode"),
                    item.get("PriceCode"),
                    item.get("LevelPriceCode"),
                    item.get("OldItemCode"),
                    item.get("ItemTypeID"),
                    item.get("ItemName"),
                    item.get("Strength"),
                    item.get("Dosage"),
                    item.get("PackageID"),
                    item.get("SchemeID"),
                    item.get("FacilityLevelCode"),
                    item.get("UnitPrice"),
                    item.get("IsRestricted"),
                    item.get("MaximumQuantity"),
                    item.get("AvailableInLevels"),
                    item.get("PractitionerQualifications"),
                    item.get("IsActive"),
                    time_stamp,
                    time_stamp,
                    user,
                    user
                ))
            frappe.db.sql('''
                INSERT INTO `tabNHIF Price Package`
                (
                    `name`, `facilitycode`, `time_stamp`, `log_name`, `itemcode`, `pricecode`,
                    `levelpricecode`, `olditemcode`, `itemtypeid`, `itemname`, `strength`, 
                    `dosage`, `packageid`, `schemeid`, `facilitylevelcode`, `unitprice`, 
                    `isrestricted`, `maximumquantity`, `availableinlevels`, 
                    `practitionerqualifications`, `IsActive`, `creation`, `modified`,
                    `modified_by`, `owner`
                )
                VALUES {}
            '''.format(', '.join(['%s'] * len(insert_data))), tuple(insert_data))
            insert_data = []
            for item in data.get("ExcludedServices"):
                insert_data.append((
                    frappe.generate_hash("", 20),
                    facility_code,
                    time_stamp,
                    log_name,
                    item.get("ItemCode"),
                    item.get("SchemeID"),
                    item.get("SchemeName"),
                    item.get("ExcludedForProducts"),
                    time_stamp,
                    time_stamp,
                    user,
                    user
                ))
            frappe.db.sql('''
                INSERT INTO `tabNHIF Excluded Services`
                (
                    `name`, `facilitycode`, `time_stamp`, `log_name`, `itemcode`, `schemeid`,
                    `schemename`, `excludedforproducts`, `creation`, `modified`,
                    `modified_by`, `owner`
                )
                VALUES {}
            '''.format(', '.join(['%s'] * len(insert_data))), tuple(insert_data))
            frappe.db.commit()
            process_prices_list(company)
            process_insurance_coverages()
            return data


def process_prices_list(company):
    facility_code = frappe.get_value(
        "Company NHIF Settings", company, "facility_code")
    currency = frappe.get_value("Company", company, "default_currency")
    schemeid_list = frappe.db.sql(
        '''
            SELECT schemeid from `tabNHIF Price Package`
                WHERE facilitycode = {0}
                GROUP BY schemeid
        '''.format(facility_code),
        as_dict=1
    )

    for scheme in schemeid_list:
        price_list_name = "NHIF-" + scheme.schemeid
        if not frappe.db.exists("Price List", price_list_name):
            price_list_doc = frappe.new_doc("Price List")
            price_list_doc.price_list_name = price_list_name
            price_list_doc.currency = currency
            price_list_doc.buying = 0
            price_list_doc.selling = 1
            price_list_doc.save(ignore_permissions=True)

    item_list = frappe.db.sql(
        '''
            SELECT ref_code, parent as item_code from `tabItem Customer Detail`
                WHERE customer_name = 'NHIF'
                GROUP by ref_code , parent
        ''',
        as_dict=1
    )

    for item in item_list:
        for scheme in schemeid_list:
            schemeid = scheme.schemeid
            price_list_name = "NHIF-" + schemeid
            package_list = frappe.db.sql(
                '''
                    SELECT schemeid, itemcode, unitprice, isactive, count(*) 
                    FROM `tabNHIF Price Package` 
                    WHERE facilitycode = {0} and schemeid = {1} and itemcode = {2}
                    GROUP by itemcode , schemeid
                    HAVING count(*) = 1
                '''.format(facility_code, schemeid, item.ref_code),
                as_dict=1
            )
            if len(package_list) > 0:
                for package in package_list:
                    item_price_list = frappe.get_all("Item Price",
                                                     filters={
                                                         "price_list": price_list_name,
                                                         "item_code": item.item_code,
                                                         "currency": currency,
                                                         "selling": 1
                                                     },
                                                     fields=[
                                                         "name", "price_list_rate"]
                                                     )
                    if len(item_price_list) > 0:
                        for price in item_price_list:
                            if int(package.isactive) == 1:
                                if float(price.price_list_rate) != float(package.unitprice):
                                    # delete Item Price if no package.unitprice or it is 0
                                    if not float(package.unitprice) or float(package.unitprice) == 0:
                                        frappe.delete_doc(
                                            "Item Price", price.name)
                                    else:
                                        frappe.set_value(
                                            "Item Price", price.name, "price_list_rate", float(package.unitprice))
                            else:
                                frappe.delete_doc("Item Price", price.name)

                    elif int(package.isactive) == 1:
                        item_price_doc = frappe.new_doc("Item Price")
                        item_price_doc.item_code = item.item_code
                        item_price_doc.price_list = price_list_name
                        item_price_doc.currency = currency
                        item_price_doc.price_list_rate = float(
                            package.unitprice)
                        item_price_doc.buying = 0
                        item_price_doc.selling = 1
                        item_price_doc.save(ignore_permissions=True)


def get_insurance_coverage_items():
    items_list = frappe.db.sql(
        '''
            SELECT 'Appointment Type' as dt, m.name as healthcare_service_template, icd.ref_code, icd.parent as item_code
                FROM `tabItem Customer Detail` icd
                INNER JOIN `tabItem` i ON i.name = icd.parent and i.disabled = 0
                INNER JOIN `tabAppointment Type` m ON icd.parent = m.out_patient_consulting_charge_item
                WHERE icd.customer_name = 'NHIF'
                GROUP BY dt, m.name, icd.ref_code , icd.parent
            UNION ALL
            SELECT 'Appointment Type' as dt, m.name as healthcare_service_template, icd.ref_code, icd.parent as item_code
                FROM `tabItem Customer Detail` icd
                INNER JOIN `tabItem` i ON i.name = icd.parent and i.disabled = 0
                INNER JOIN `tabAppointment Type` m ON icd.parent = m.inpatient_visit_charge_item
                WHERE icd.customer_name = 'NHIF'
                GROUP BY dt, m.name, icd.ref_code , icd.parent
            UNION ALL
            SELECT 'Clinical Procedure Template' as dt, m.name as healthcare_service_template, icd.ref_code, icd.parent as item_code
                FROM `tabItem Customer Detail` icd
                INNER JOIN `tabItem` i ON i.name = icd.parent and i.disabled = 0
                INNER JOIN `tabClinical Procedure Template` m ON icd.parent = m.item
                WHERE icd.customer_name = 'NHIF'
                GROUP BY dt, m.name, icd.ref_code , icd.parent
            UNION ALL
            SELECT 'Therapy Type' as dt, m.name as healthcare_service_template, icd.ref_code, icd.parent as item_code
                FROM `tabItem Customer Detail` icd
                INNER JOIN `tabItem` i ON i.name = icd.parent and i.disabled = 0
                INNER JOIN `tabTherapy Type` m ON icd.parent = m.item
                WHERE icd.customer_name = 'NHIF'
                GROUP BY dt, m.name, icd.ref_code , icd.parent
            UNION ALL
            SELECT 'Medication' as dt, m.name as healthcare_service_template, icd.ref_code, icd.parent as item_code
                FROM `tabItem Customer Detail` icd
                INNER JOIN `tabItem` i ON i.name = icd.parent and i.disabled = 0
                INNER JOIN `tabMedication` m ON icd.parent = m.item
                WHERE icd.customer_name = 'NHIF'
                GROUP BY dt, m.name, icd.ref_code , icd.parent
            UNION ALL
            SELECT 'Lab Test Template' as dt, m.name as healthcare_service_template, icd.ref_code, icd.parent as item_code
                FROM `tabItem Customer Detail` icd
                INNER JOIN `tabItem` i ON i.name = icd.parent and i.disabled = 0
                INNER JOIN `tabLab Test Template` m ON icd.parent = m.item
                WHERE icd.customer_name = 'NHIF'
                GROUP BY dt, m.name, icd.ref_code , icd.parent
            UNION ALL
            SELECT 'Radiology Examination Template' as dt, m.name as healthcare_service_template, icd.ref_code, icd.parent as item_code
                FROM `tabItem Customer Detail` icd
                INNER JOIN `tabItem` i ON i.name = icd.parent and i.disabled = 0
                INNER JOIN `tabRadiology Examination Template` m ON icd.parent = m.item
                WHERE icd.customer_name = 'NHIF'
                GROUP BY dt, m.name, icd.ref_code , icd.parent
            UNION ALL
            SELECT 'Healthcare Service Unit Type' as dt, m.name as healthcare_service_template, icd.ref_code, icd.parent as item_code
                FROM `tabItem Customer Detail` icd
                INNER JOIN `tabItem` i ON i.name = icd.parent and i.disabled = 0
                INNER JOIN `tabHealthcare Service Unit Type` m ON icd.parent = m.item
                WHERE icd.customer_name = 'NHIF'
                GROUP BY dt, m.name, icd.ref_code , icd.parent
        ''',
        as_dict=1
    )
    return items_list


def get_excluded_services(itemcode):
    excluded_services = ""
    excluded_services_list = frappe.get_all(
        "NHIF Excluded Services",
        filters={
            "itemcode": itemcode
        }
    )
    if len(excluded_services_list) > 0:
        excluded_services = excluded_services_list[0].excludedforproducts
    return excluded_services


def process_insurance_coverages():
    items_list = get_insurance_coverage_items()

    coverage_plan_list = frappe.get_all(
        "Healthcare Insurance Coverage Plan",
        filters={"insurance_company_name": "NHIF", "is_active": 1}
    )

    for plan in coverage_plan_list:
        insert_data = []
        time_stamp = now()
        user = frappe.session.user
        for item in items_list:
            excluded_services = get_excluded_services(item.ref_code)
            if excluded_services:
                if plan.name in excluded_services:
                    continue
            doc = frappe.new_doc("Healthcare Service Insurance Coverage")
            doc.healthcare_service = item.dt
            doc.healthcare_service_template = item.healthcare_service_template
            doc.healthcare_insurance_coverage_plan = plan.name
            doc.coverage = 100
            doc.end_date = "2099-12-31"
            doc.is_active = 1
            doc.discount = 0
            doc.maximum_number_of_claims = 0
            set_new_name(doc)

            insert_data.append((
                doc.approval_mandatory_for_claim,
                doc.coverage,
                time_stamp,
                doc.discount,
                doc.end_date,
                doc.healthcare_insurance_coverage_plan,
                doc.healthcare_service,
                doc.healthcare_service_template,
                doc.is_active,
                doc.manual_approval_only,
                doc.maximum_number_of_claims,
                time_stamp,
                user,
                doc.name,
                doc.naming_series,
                user,
                doc.start_date,
                1
            ))

        frappe.db.sql(
            "DELETE FROM `tabHealthcare Service Insurance Coverage` WHERE is_auto_generated = 1 AND healthcare_insurance_coverage_plan = '{0}'".format(plan.name))

        frappe.db.sql('''
            INSERT INTO `tabHealthcare Service Insurance Coverage`
            (
                `approval_mandatory_for_claim`, 
                `coverage`, 
                `creation`, 
                `discount`, 
                `end_date`, 
                `healthcare_insurance_coverage_plan`, 
                `healthcare_service`, 
                `healthcare_service_template`, 
                `is_active`, 
                `manual_approval_only`, 
                `maximum_number_of_claims`, 
                `modified`, 
                `modified_by`, 
                `name`, 
                `naming_series`, 
                `owner`, 
                `start_date`,
                `is_auto_generated`
            )
            VALUES {}
        '''.format(', '.join(['%s'] * len(insert_data))), tuple(insert_data))
