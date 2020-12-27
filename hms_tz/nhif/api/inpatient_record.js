frappe.ui.form.on('Inpatient Record', {
    setup: function(frm) {

    },

    refresh: function(frm) {
        refresh_field('drug_prescription');
        refresh_field('lab_test_prescription');
        if(frm.doc.patient){
            show_patient_vital_charts(frm.doc.patient, frm, "bp", "mmHg", "Blood Pressure");
        }
        else{
            frm.fields_dict.patient_vitals.html("<div align='center'>Please select Patient.</div>");
        }
    },
    on_submit: function (frm) {
        if (!frm.doc.inpatient_record_final_diagnosis) {
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
    inpatient_record_preliminary_diagnosis: function(frm) {
		set_medical_code(frm)
    },
    inpatient_record_final_diagnosis: function(frm) {
		set_medical_code(frm)
    },

});


frappe.ui.form.on('Codification Table', {
    inpatient_record_preliminary_diagnosis_add: function (frm) {
        set_medical_code(frm)
    },
    inpatient_record_preliminary_diagnosis_remove: function (frm) {
        set_medical_code(frm)
    },
    inpatient_record_final_diagnosis_add: function (frm) {
        set_medical_code(frm)
    },
    inpatient_record_final_diagnosis_remove: function (frm) {
        set_medical_code(frm)
    },
    medical_code(frm, cdt, cdn) {
        set_medical_code(frm)
    }
});

var get_preliminary_diagnosis = function (frm){
    const diagnosis_list = [];
    if (frm.doc.inpatient_record_preliminary_diagnosis) {
        frm.doc.inpatient_record_preliminary_diagnosis.forEach(element => {
            diagnosis_list.push(element.medical_code)
        });
        return diagnosis_list
    }
}

var get_final_diagnosis = function (frm){
    const diagnosis_list = [];
    if (frm.doc.inpatient_record_final_diagnosis) {
        frm.doc.inpatient_record_final_diagnosis.forEach(element => {
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
        if (row.prescribe || !row.lab_test_code) {return}
        validate_stock_item(frm, row.lab_test_code)
    },
    override_subscription: function(frm, cdt, cdn) {
        let row = frappe.get_doc(cdt, cdn);
        if (row.override_subscription == 0) {
            frappe.model.set_value(cdt, cdn, "prescribe", 0)
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
        if (row.prescribe || !row.radiology_examination_template) {return}
        validate_stock_item(frm, row.radiology_examination_template)
    },
    override_subscription: function(frm, cdt, cdn) {
        let row = frappe.get_doc(cdt, cdn);
        if (row.override_subscription == 0) {
            frappe.model.set_value(cdt, cdn, "prescribe", 0)
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
        if (row.prescribe || !row.procedure) {return}
        validate_stock_item(frm, row.procedure)
    },
    override_subscription: function(frm, cdt, cdn) {
        let row = frappe.get_doc(cdt, cdn);
        if (row.override_subscription == 0) {
            frappe.model.set_value(cdt, cdn, "prescribe", 0)
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
        if (row.prescribe || !row.drug_code) {return}
        validate_stock_item(frm, row.drug_code, row.quantity)
    },
    quantity: function(frm, cdt, cdn) {
        let row = frappe.get_doc(cdt, cdn);
        if (row.prescribe || !row.drug_code) {return}
        validate_stock_item(frm, row.drug_code, row.quantity)
    },
    override_subscription: function(frm, cdt, cdn) {
        let row = frappe.get_doc(cdt, cdn);
        if (row.override_subscription == 0) {
            frappe.model.set_value(cdt, cdn, "prescribe", 0)
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
        if (row.prescribe || !row.therapy_type) {return}
        validate_stock_item(frm, row.therapy_type)
    },
    override_subscription: function(frm, cdt, cdn) {
        let row = frappe.get_doc(cdt, cdn);
        if (row.override_subscription == 0) {
            frappe.model.set_value(cdt, cdn, "prescribe", 0)
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

var show_patient_vital_charts = function(patient, frm, btn_show_id, pts, title) {
frappe.call({
    method: "hms_tz.hms_tz.utils.get_patient_vitals",
    args:{
        patient: patient
    },
    callback: function(r) {
        if (r.message){
            var vitals_section_template =
                            "<div class='col-sm-12'> \
                                <div class='col-sm-12 show_chart_btns' align='center'> \
                                </div> \
                                <div class='col-sm-12 patient_vital_charts'> \
                                </div> \
                            </div>";
            var show_chart_btns_html = "<div style='padding-top:5px;'><a class='btn btn-default btn-xs btn-show-chart' \
            data-show-chart-id='bp' data-pts='mmHg' data-title='Blood Pressure'>Blood Pressure</a>\
            <a class='btn btn-default btn-xs btn-show-chart' data-show-chart-id='pulse_rate' \
            data-pts='per Minutes' data-title='Respiratory/Pulse Rate'>Respiratory/Pulse Rate</a>\
            <a class='btn btn-default btn-xs btn-show-chart' data-show-chart-id='temperature' \
            data-pts='°C or °F' data-title='Temperature'>Temperature</a>\
            <a class='btn btn-default btn-xs btn-show-chart' data-show-chart-id='bmi' \
            data-pts='' data-title='BMI'>BMI</a></div>";
            frm.fields_dict.patient_vitals.$wrapper.html(vitals_section_template);
            frm.fields_dict.patient_vitals.$wrapper.find('.show_chart_btns').html(show_chart_btns_html);
            // me.page.main.find(".show_chart_btns").html(show_chart_btns_html);
            //handler for buttons
            frm.fields_dict.patient_vitals.$wrapper.find('.btn-show-chart').on("click", function() {
                var	btn_show_id = $(this).attr("data-show-chart-id"), pts = $(this).attr("data-pts");
                var title = $(this).attr("data-title");
                show_patient_vital_charts(frm.doc.patient, frm, btn_show_id, pts, title);
            });
            var data = r.message;
            let labels = [], datasets = [];
            let bp_systolic = [], bp_diastolic = [], temperature = [];
            let pulse = [], respiratory_rate = [], bmi = [], height = [], weight = [];
            for(var i=0; i<data.length; i++){
                labels.push(data[i].signs_date+"||"+data[i].signs_time);
                if(btn_show_id=="bp"){
                    bp_systolic.push(data[i].bp_systolic);
                    bp_diastolic.push(data[i].bp_diastolic);
                }
                if(btn_show_id=="temperature"){
                    temperature.push(data[i].temperature);
                }
                if(btn_show_id=="pulse_rate"){
                    pulse.push(data[i].pulse);
                    respiratory_rate.push(data[i].respiratory_rate);
                }
                if(btn_show_id=="bmi"){
                    bmi.push(data[i].bmi);
                    height.push(data[i].height);
                    weight.push(data[i].weight);
                }
            }
            if(btn_show_id=="temperature"){
                datasets.push({name: "Temperature", values: temperature, chartType:'line'});
            }
            if(btn_show_id=="bmi"){
                datasets.push({name: "BMI", values: bmi, chartType:'line'});
                datasets.push({name: "Height", values: height, chartType:'line'});
                datasets.push({name: "Weight", values: weight, chartType:'line'});
            }
            if(btn_show_id=="bp"){
                datasets.push({name: "BP Systolic", values: bp_systolic, chartType:'line'});
                datasets.push({name: "BP Diastolic", values: bp_diastolic, chartType:'line'});
            }
            if(btn_show_id=="pulse_rate"){
                datasets.push({name: "Heart Rate / Pulse", values: pulse, chartType:'line'});
                datasets.push({name: "Respiratory Rate", values: respiratory_rate, chartType:'line'});
            }
            new frappe.Chart( ".patient_vital_charts", {
                data: {
                    labels: labels,
                    datasets: datasets
                },

                title: title,
                type: 'axis-mixed', // 'axis-mixed', 'bar', 'line', 'pie', 'percentage'
                height: 200,
                colors: ['purple', '#ffa3ef', 'light-blue'],

                tooltipOptions: {
                    formatTooltipX: d => (d + '').toUpperCase(),
                    formatTooltipY: d => d + ' ' + pts,
                }
            });
        }else{
                frm.fields_dict.patient_vitals.html("<div align='center'>No records found</div>");
        }
    }
});
};
