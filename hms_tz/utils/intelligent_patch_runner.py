import frappe
import importlib
from frappe.custom.doctype.custom_field.custom_field import create_custom_field


class PatchLogger:
    def __init__(self):
        self.created = []
        self.skipped = []
        self.updated = []
        self.failed = []

    def report(self):
        print("\n\n========== PATCH REPORT ==========")

        print("\nCREATED:")
        for i in self.created:
            print("  ✔", i)

        print("\nUPDATED:")
        for i in self.updated:
            print("  ↺", i)

        print("\nSKIPPED:")
        for i in self.skipped:
            print("  →", i)

        print("\nFAILED:")
        for i in self.failed:
            print("  ✖", i)

        print("\n==================================\n")


logger = PatchLogger()


# -------------------------------------------------
# SAFE CUSTOM FIELD CREATOR
# -------------------------------------------------
def smart_create_custom_field(doctype, fielddict):
    fieldname = fielddict.get("fieldname")

    existing = frappe.db.get_value(
        "Custom Field",
        {"dt": doctype, "fieldname": fieldname},
        ["name", "fieldtype", "label", "options"],
        as_dict=True,
    )

    if not existing:
        create_custom_field(doctype, fielddict)
        logger.created.append(f"{doctype}.{fieldname}")
        return

    # compare and update differences
    changed = False
    doc = frappe.get_doc("Custom Field", existing.name)

    for key in ["fieldtype", "label", "options"]:
        new_val = fielddict.get(key)
        if new_val and getattr(doc, key) != new_val:
            setattr(doc, key, new_val)
            changed = True

    if changed:
        doc.save()
        logger.updated.append(f"{doctype}.{fieldname}")
    else:
        logger.skipped.append(f"{doctype}.{fieldname}")


# -------------------------------------------------
# SAFE PROPERTY SETTER
# -------------------------------------------------
def smart_property_setter(doc_type, field_name, prop, value, property_type="Data"):
    existing = frappe.db.get_value(
        "Property Setter",
        {
            "doc_type": doc_type,
            "field_name": field_name,
            "property": prop,
        },
        ["name", "value"],
        as_dict=True,
    )

    if not existing:
        frappe.get_doc(
            dict(
                doctype="Property Setter",
                doc_type=doc_type,
                field_name=field_name,
                property=prop,
                value=value,
                property_type=property_type,
            )
        ).insert(ignore_permissions=True)

        logger.created.append(f"{doc_type}.{field_name}.{prop}")
        return

    if str(existing.value) != str(value):
        doc = frappe.get_doc("Property Setter", existing.name)
        doc.value = value
        doc.save()
        logger.updated.append(f"{doc_type}.{field_name}.{prop}")
    else:
        logger.skipped.append(f"{doc_type}.{field_name}.{prop}")


# -------------------------------------------------
# PATCH RUNNER
# -------------------------------------------------
def run_patch(module_path):
    try:
        module = importlib.import_module(module_path)

        # inject smart functions so patch uses them automatically
        module.create_custom_field = smart_create_custom_field
        module.make_property_setter = smart_property_setter

        if hasattr(module, "execute"):
            print("Running:", module_path)
            module.execute()

    except Exception:
        logger.failed.append(module_path)
        frappe.log_error(frappe.get_traceback(), f"Patch Failed: {module_path}")


# -------------------------------------------------
# MAIN EXECUTION
# -------------------------------------------------
def execute():

    patches = frappe.get_all(
        "Patch Log",
        filters={"applied": 0},
        pluck="patch"
    )

    if not patches:
        print("No pending patches.")
        return

    for patch in patches:
        run_patch(patch)

    logger.report()
