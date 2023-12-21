frappe.query_reports["Monthly NHIF Detail"] = {
    "filters": [
        {
            "fieldname": "company",
            "label": __("Company"),
            "fieldtype": "Link",
            "options": "Company",
            "default": frappe.defaults.get_user_default("Company"),
            "reqd": 1,
        },
        {
            "fieldname": "claim_month",
            "label": __("Claim Month"),
            "fieldtype": "Int",
            "reqd": 1
        },
        {
            "fieldname": "claim_year",
            "label": __("Claim Year"),
            "fieldtype": "Int",
            "reqd": 1
        },
        {
            "fieldname": "drafts_unclaimable",
            "label": __("Show Drafts/Unclaimable"),
            "fieldtype": "Check",
        }
    ]
};