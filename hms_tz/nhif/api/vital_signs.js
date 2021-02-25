frappe.ui.form.on('Vital Signs', {
    refresh: function (frm) {
        if (frm.doc.patient) {
            show_patient_vital_charts(frm.doc.patient, frm, "bp", "mmHg", "Blood Pressure");
        }
        else {
            frm.fields_dict.patient_vitals.html("<div align='center'>Please select Patient.</div>");
        }
    },
    height_in_cm: function (frm) {
        frm.set_value("height", frm.doc.height_in_cm / 100)
    },
    patient: function (frm) {
        if (frm.doc.patient) {
            show_patient_vital_charts(frm.doc.patient, frm, "bp", "mmHg", "Blood Pressure");
        }
        else {
            frm.fields_dict.patient_vitals.html("<div align='center'>Please select Patient.</div>");
        }
    },
})

var show_patient_vital_charts = function (patient, frm, btn_show_id, pts, title) {
    frappe.call({
        method: "hms_tz.hms_tz.utils.get_patient_vitals",
        args: {
            patient: patient
        },
        callback: function (r) {
            if (r.message) {
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
                frm.fields_dict.patient_vitals.$wrapper.find('.btn-show-chart').on("click", function () {
                    var btn_show_id = $(this).attr("data-show-chart-id"), pts = $(this).attr("data-pts");
                    var title = $(this).attr("data-title");
                    show_patient_vital_charts(frm.doc.patient, frm, btn_show_id, pts, title);
                });
                var data = r.message;
                let labels = [], datasets = [];
                let bp_systolic = [], bp_diastolic = [], temperature = [];
                let pulse = [], respiratory_rate = [], bmi = [], height = [], weight = [];
                for (var i = 0; i < data.length; i++) {
                    labels.push(data[i].signs_date + "||" + data[i].signs_time);
                    if (btn_show_id == "bp") {
                        bp_systolic.push(data[i].bp_systolic);
                        bp_diastolic.push(data[i].bp_diastolic);
                    }
                    if (btn_show_id == "temperature") {
                        temperature.push(data[i].temperature);
                    }
                    if (btn_show_id == "pulse_rate") {
                        pulse.push(data[i].pulse);
                        respiratory_rate.push(data[i].respiratory_rate);
                    }
                    if (btn_show_id == "bmi") {
                        bmi.push(data[i].bmi);
                        height.push(data[i].height_in_cm);
                        weight.push(data[i].weight);
                    }
                }
                if (btn_show_id == "temperature") {
                    datasets.push({ name: "Temperature", values: temperature, chartType: 'line' });
                }
                if (btn_show_id == "bmi") {
                    datasets.push({ name: "BMI", values: bmi, chartType: 'line' });
                    datasets.push({ name: "Height", values: height, chartType: 'line' });
                    datasets.push({ name: "Weight", values: weight, chartType: 'line' });
                }
                if (btn_show_id == "bp") {
                    datasets.push({ name: "BP Systolic", values: bp_systolic, chartType: 'line' });
                    datasets.push({ name: "BP Diastolic", values: bp_diastolic, chartType: 'line' });
                }
                if (btn_show_id == "pulse_rate") {
                    datasets.push({ name: "Heart Rate / Pulse", values: pulse, chartType: 'line' });
                    datasets.push({ name: "Respiratory Rate", values: respiratory_rate, chartType: 'line' });
                }
                new frappe.Chart(".patient_vital_charts", {
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
            } else {
                frm.fields_dict.patient_vitals.html("<div align='center'>No records found</div>");
            }
        }
    });
};

