frappe.ui.form.on('Patient Encounter', {
    on_submit: function (frm) {
        if (!frm.doc.patient_encounter_final_diagnosis) {
            frappe.throw(__("Final diagnosis mandatory before submit"))
        }
    },
    validate: function (frm) {
        validate_medical_code(frm)
    },
    onload: function (frm) {
        set_medical_code(frm)
        add_btn_final(frm)
        duplicate(frm)
    },
    refresh: function(frm) {
        set_medical_code(frm)
        duplicate(frm)
    },
    patient_encounter_preliminary_diagnosis: function(frm) {
		set_medical_code(frm)
    },
    patient_encounter_final_diagnosis: function(frm) {
		set_medical_code(frm)
    },
    get_chronic_diagnosis: function(frm) {
        if (frm.doc.docstatus == 1) {
            return
        }
        frappe.call({
            method: 'hms_tz.nhif.api.patient_encounter.get_chronic_diagnosis',
            args: {
                'patient': frm.doc.patient,
            },
            callback: function (data) {
                if (data.message) {
                    if (data.message.length == 0) {
                        frappe.show_alert({
                            message:__(`There is no Chronic Diagnosis`),
                            indicator:'red'
                        }, 5);
                        return
                    }
                    data.message.forEach(element => {
                        const row_idx = frm.doc.patient_encounter_preliminary_diagnosis.findIndex(x => x.medical_code === element.medical_code)
                        if (row_idx === -1) {
                            let row = frappe.model.add_child(frm.doc, "Codification Table", "patient_encounter_preliminary_diagnosis")
                            row.medical_code = element.medical_code;
                            row.code = element.code;
                            row.description = element.description;
                            frappe.show_alert({
                                message:__(`Medical Code '${element.medical_code}' added successfully`),
                                indicator:'green'
                            }, 5);
                        } else {
                            frappe.show_alert({
                                message:__(`Medical Code '${element.medical_code}' already exists`),
                                indicator:'red'
                            }, 5);
                        }
                    })
                    refresh_field('patient_encounter_preliminary_diagnosis')
                    set_medical_code(frm)
                }
            }
        });
    },
    get_chronic_medications: function(frm) {
        if (frm.doc.docstatus == 1) {
            return
        }
        frappe.call({
            method: 'hms_tz.nhif.api.patient_encounter.get_chronic_medications',
            args: {
                'patient': frm.doc.patient,
            },
            callback: function (data) {
                if (data.message) {
                    if (data.message.length == 0) {
                        frappe.show_alert({
                            message:__(`There is no Chronic Medications`),
                            indicator:'red'
                        }, 5);
                        return
                    }
                    data.message.forEach(element => {
                        const row_idx = frm.doc.drug_prescription.findIndex(x => x.drug_code === element.drug_code)
                        if (row_idx === -1) {
                            let row = frappe.model.add_child(frm.doc, "Drug Prescription", "drug_prescription")
                            row.drug_code = element.drug_code;
                            row.drug_name = element.drug_name;
                            row.dosage = element.dosage;
                            row.period = element.period;
                            row.dosage_form = element.dosage_form;
                            row.comment = element.comment;
                            row.usage_interval = element.usage_interval;
                            row.interval = element.interval;
                            row.interval_uom = element.interval_uom;
                            row.update_schedule = element.update_schedule;
                            row.intent = element.intent;
                            row.quantity = element.quantity;
                            row.sequence = element.sequence;
                            row.expected_date = element.expected_date;
                            row.as_needed = element.as_needed;
                            row.patient_instruction = element.patient_instruction;
                            row.replaces = element.replaces;
                            row.priority = element.priority;
                            row.occurrence = element.occurrence;
                            row.occurence_period = element.occurence_period;
                            row.note = element.note;
                            frappe.show_alert({
                                message:__(`Drug '${element.drug_code}' added successfully`),
                                indicator:'green'
                            }, 5);
                        } else {
                            frappe.show_alert({
                                message:__(`Drug '${element.drug_code}' already exists`),
                                indicator:'red'
                            }, 5);
                        }
                    })
                    refresh_field('drug_prescription')
                }
            }
        });
    },
    copy_from_preliminary_diagnosis: function(frm) {
        if (frm.doc.docstatus == 1) {
            return
        }
        frm.doc.patient_encounter_preliminary_diagnosis.forEach(element => {
            const row_idx = frm.doc.patient_encounter_final_diagnosis.findIndex(x => x.medical_code === element.medical_code)
            if (row_idx === -1) {
                let row = frappe.model.add_child(frm.doc, "Codification Table", "patient_encounter_final_diagnosis")
                row.medical_code = element.medical_code;
                row.code = element.code;
                row.description = element.description;
                frappe.show_alert({
                    message:__(`Medical Code '${element.medical_code}' added successfully`),
                    indicator:'green'
                }, 5);
            } else {
                frappe.show_alert({
                    message:__(`Medical Code '${element.medical_code}' already exists`),
                    indicator:'red'
                }, 5);
            }
        })
        refresh_field('patient_encounter_final_diagnosis')
        set_medical_code(frm)
    },

});


frappe.ui.form.on('Codification Table', {
    patient_encounter_preliminary_diagnosis_add: function (frm) {
        set_medical_code(frm)
    },
    patient_encounter_preliminary_diagnosis_remove: function (frm) {
        set_medical_code(frm)
    },
    patient_encounter_final_diagnosis_add: function (frm) {
        set_medical_code(frm)
    },
    patient_encounter_final_diagnosis_remove: function (frm) {
        set_medical_code(frm)
    },
    medical_code(frm, cdt, cdn) {
        set_medical_code(frm)
    }
});

var get_preliminary_diagnosis = function (frm){
    const diagnosis_list = [];
    if (frm.doc.patient_encounter_preliminary_diagnosis) {
        frm.doc.patient_encounter_preliminary_diagnosis.forEach(element => {
            diagnosis_list.push(element.medical_code)
        });
        return diagnosis_list
    }
}

var get_final_diagnosis = function (frm){
    const diagnosis_list = [];
    if (frm.doc.patient_encounter_final_diagnosis) {
        frm.doc.patient_encounter_final_diagnosis.forEach(element => {
            diagnosis_list.push(element.medical_code)
        });
       return diagnosis_list
    }
}

var set_medical_code = function (frm) {
    const final_diagnosis = get_final_diagnosis(frm)
    const preliminary_diagnosis = get_preliminary_diagnosis(frm)
    frappe.meta.get_docfield("Drug Prescription", "medical_code", frm.doc.name).options = final_diagnosis;
    refresh_field("drug_prescription");

    frappe.meta.get_docfield("Lab Prescription", "medical_code", frm.doc.name).options = preliminary_diagnosis
    refresh_field("lab_test_prescription");

    frappe.meta.get_docfield("Procedure Prescription", "medical_code", frm.doc.name).options = final_diagnosis;
    refresh_field("procedure_prescription");

    frappe.meta.get_docfield("Radiology Procedure Prescription", "medical_code", frm.doc.name).options = preliminary_diagnosis;
    refresh_field("radiology_procedure_prescription");

    frappe.meta.get_docfield("Therapy Plan Detail", "medical_code", frm.doc.name).options = final_diagnosis;
    refresh_field("therapies");

    frappe.meta.get_docfield("Diet Recommendation", "medical_code", frm.doc.name).options = final_diagnosis;
    refresh_field("diet_recommendation");

    frm.refresh_fields();
}

var validate_medical_code = function (frm) {
    if (frm.doc.drug_prescription) {
        frm.doc.drug_prescription.forEach(element => {
            if (!get_final_diagnosis(frm).includes(element.medical_code)) {
                frappe.throw(__(`The medical code is not set in 'Drug Prescription' line item ${element.idx}`))
            }
        });
    }
    if (frm.doc.lab_test_prescription) {
        frm.doc.lab_test_prescription.forEach(element => {
            if (!get_preliminary_diagnosis(frm).includes(element.medical_code)) {
                frappe.throw(__(`The medical code is not set in 'Lab Prescription' line item ${element.idx}`))
            }
        });
    }
    if (frm.doc.procedure_prescription) {
        frm.doc.procedure_prescription.forEach(element => {
            if (!get_final_diagnosis(frm).includes(element.medical_code)) {
                frappe.throw(__(`The medical code is not set in 'Procedure Prescription' line item ${element.idx}`))
            }
        });
    }
    if (frm.doc.radiology_procedure_prescription) {
        frm.doc.radiology_procedure_prescription.forEach(element => {
            if (!get_preliminary_diagnosis(frm).includes(element.medical_code)) {
                frappe.throw(__(`The medical code is not set in 'Radiology Procedure Prescription' line item ${element.idx}`))
            }
        });
    }
    if (frm.doc.procedure_prescription) {
        frm.doc.procedure_prescription.forEach(element => {
            if (!get_final_diagnosis(frm).includes(element.medical_code)) {
                frappe.throw(__(`The medical code is not set in 'Therapy Plan Detail' line item ${element.idx}`))
            }
        });
    }
    if (frm.doc.diet_recommendation) {
        frm.doc.diet_recommendation.forEach(element => {
            if (!get_final_diagnosis(frm).includes(element.medical_code)) {
                frappe.throw(__(`The medical code is not set in 'Diet Recommendation' line item ${element.idx}`))
            }
        });
    }
}

var add_btn_final = function(frm) {
    if (frm.doc.docstatus==1 && frm.doc.encounter_type != 'Final') {
        frm.add_custom_button(__('Set as Final'), function() {
            frm.set_value("encounter_type", 'Final');
        });
    }
}

var duplicate = function(frm) {
    if (frm.doc.docstatus!=1 || frm.doc.encounter_type == 'Final' || frm.doc.duplicate == 1) {
        return
    }
    frm.add_custom_button(__('Duplicate'), function() {
        frm.save()
        frappe.call({
            method: 'hms_tz.nhif.api.patient_encounter.duplicate_encounter',
            args: {
                'encounter': frm.doc.name
            },
            callback: function (data) {
                if (data.message) {
                    frappe.set_route('Form', 'Patient Encounter', data.message);
                }
            }
        });
    });
}

frappe.ui.form.on('Lab Prescription', {
    lab_test_code: function(frm, cdt, cdn) {
        let row = frappe.get_doc(cdt, cdn);
        if (row.prescribe || !row.lab_test_code) {return}
        validate_stock_item(frm, row.lab_test_code)
    },
    prescribe: function(frm, cdt, cdn) {
        let row = frappe.get_doc(cdt, cdn);
        if (row.prescribe || !row.lab_test_code) {
            frappe.model.set_value(cdt, cdn, "override_subscription", 0)
        }
    },
    override_subscription: function(frm, cdt, cdn) {
        let row = frappe.get_doc(cdt, cdn);
        if (row.override_subscription) {
            frappe.model.set_value(cdt, cdn, "prescribe", 0)
            validate_stock_item(frm, row.lab_test_code)
        }
    },
});

frappe.ui.form.on('Radiology Procedure Prescription', {
    radiology_examination_template: function(frm, cdt, cdn) {
        let row = frappe.get_doc(cdt, cdn);
        if (row.prescribe || !row.radiology_examination_template) {return}
        validate_stock_item(frm, row.radiology_examination_template)
    },
    prescribe: function(frm, cdt, cdn) {
        let row = frappe.get_doc(cdt, cdn);
        if (row.prescribe || !row.radiology_examination_template) {
            frappe.model.set_value(cdt, cdn, "override_subscription", 0)
        }
    },
    override_subscription: function(frm, cdt, cdn) {
        let row = frappe.get_doc(cdt, cdn);
        if (row.override_subscription) {
            frappe.model.set_value(cdt, cdn, "prescribe", 0)
            validate_stock_item(frm, row.radiology_examination_template)
        }
    },
});

frappe.ui.form.on('Procedure Prescription', {
    procedure: function(frm, cdt, cdn) {
        let row = frappe.get_doc(cdt, cdn);
        if (row.prescribe || !row.procedure) {return}
        validate_stock_item(frm, row.procedure)
    },
    prescribe: function(frm, cdt, cdn) {
        let row = frappe.get_doc(cdt, cdn);
        if (row.prescribe || !row.procedure) {
            frappe.model.set_value(cdt, cdn, "override_subscription", 0)
        }
    },
    override_subscription: function(frm, cdt, cdn) {
        let row = frappe.get_doc(cdt, cdn);
        if (row.override_subscription) {
            frappe.model.set_value(cdt, cdn, "prescribe", 0)
            validate_stock_item(frm, row.procedure)
        }
    },
});

frappe.ui.form.on('Drug Prescription', {
    drug_code: function(frm, cdt, cdn) {
        let row = frappe.get_doc(cdt, cdn);
        if (row.prescribe || !row.drug_code) {return}
        validate_stock_item(frm, row.drug_code, row.quantity)
    },
    prescribe: function(frm, cdt, cdn) {
        let row = frappe.get_doc(cdt, cdn);
        if (row.prescribe || !row.drug_code) {
            frappe.model.set_value(cdt, cdn, "override_subscription", 0)
        }
    },
    quantity: function(frm, cdt, cdn) {
        let row = frappe.get_doc(cdt, cdn);
        if (row.prescribe || !row.drug_code) {return}
        validate_stock_item(frm, row.drug_code, row.quantity)
    },
    override_subscription: function(frm, cdt, cdn) {
        let row = frappe.get_doc(cdt, cdn);
        if (row.override_subscription) {
            frappe.model.set_value(cdt, cdn, "prescribe", 0)
            validate_stock_item(frm, row.drug_code, row.quantity)
        }
    },
});

frappe.ui.form.on('Therapy Plan Detail', {
    therapy_type: function(frm, cdt, cdn) {
        let row = frappe.get_doc(cdt, cdn);
        if (row.prescribe || !row.therapy_type) {return}
        validate_stock_item(frm, row.therapy_type)
    },
    prescribe: function(frm, cdt, cdn) {
        let row = frappe.get_doc(cdt, cdn);
        if (row.prescribe || !row.therapy_type) {
            frappe.model.set_value(cdt, cdn, "override_subscription", 0)
        }
    },
    override_subscription: function(frm, cdt, cdn) {
        let row = frappe.get_doc(cdt, cdn);
        if (row.override_subscription) {
            frappe.model.set_value(cdt, cdn, "prescribe", 0)
            validate_stock_item(frm, row.therapy_type)
        }
    },
});


var validate_stock_item = function(frm, medication_name, qty=1) {
    frappe.call({
        method: 'hms_tz.nhif.api.patient_encounter.validate_stock_item',
        args: {
            'medication_name': medication_name,
            'qty': qty,
            'healthcare_service_unit': frm.doc.healthcare_service_unit
        },
        callback: function (data) {
            if (data.message) {
                // console.log(data.message)
            }
        }
    });
};