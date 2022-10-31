$(document).ready(function() {
    if ($('div').is('.content')){
        let patients = ""
        let data = JSON.parse(document.getElementById('data').textContent)
        patients = data['patients']

        fillTable(patients)
        fillPhoneData(data)

        $('.data-filter').click(function() {
            $.ajaxSetup({
                headers: {
                    "X-CSRFToken": document.querySelector('[name=csrfmiddlewaretoken]').value,
                }
            });

            let day1 = $('.day-1').val()
            let day2 = $('.day-2').val()
            let error_msg = $('.invalid-feedback')
            error_msg.css({'display': 'none'})

            if (day1.length === 0 || day2.length === 0){
                error_msg.css({'display': 'block'})
            }
            else {
                let formData = new FormData()
                formData.append("day1", day1)
                formData.append("day2", day2)
                formData.append("action", "date-filter")
                $.ajax({
                    method: 'POST',
                    url: "/",
                    data: formData,
                    processData: false,
                    contentType: false,
                    success: function(resp){
                        let info = resp.data
                        $(".patient tr").remove()
                        patients = info['patients']
                        fillTable(patients)
                        fillPhoneData(info)
                    },
                    error: function (error){
                        console.log(error)
                    }

                });
            }
        })

        sortData('.hc', 'clinician__healthy_facility__name', patients)
        sortData('.gender', 'gender', patients)
        sortData('.pneumonia', 'none', patients)
        sortData('.acute', 'diagnosis_2', patients)
        sortData('.fever', 'diagnosis_4', patients)
        sortData('.febrile', 'diagnosis_5', patients)
        sortData('.hiv', 'hiv_status', patients)
        sortData('.breathing', 'breathing_rate', patients)

    }
})

function fillTable(data){
     $.each(data, function(index, value){
         $(".patient").append("<tr><td>" + value['age2'] + "</td>" +
                                     "<td>"+ value['weight'] +"</td>" +
                                     "<td>"+ value['muac'] +"</td>" +
                                     "<td>"+ value['symptoms'] +"</td>" +
                                     "<td>"+ value['difficulty_breathing'] +"</td>" +
                                     "<td>"+ value['days_with_breathing_difficulties'] +"</td>" +
                                     "<td>"+ value['temperature'] +"</td>" +
                                     "<td>"+ value['blood_oxygen_saturation'] +"</td>" +
                                     "<td>"+ value['respiratory_rate'] +"</td>" +
                                     "<td>"+ value['stridor'] +"</td>" +
                                     "<td>"+ value['nasal_flaring'] +"</td>" +
                                     "<td>"+ value['wheezing'] +"</td>" +
                                     "<td>"+ value['chest_indrawing'] +"</td>" +
                                     "<td>"+ value['duration'] +"</td>" +
                                "</tr>");
    })
}

function fillPhoneData(data){
    $('.active-users').text(data["active_users"])
    $('.app-loaded').text(data["app_opening"])
    $('.learn-loaded').text(data["learn"])
    $('.rr-counter').text(data["rr_counter"])

    $('.clinicians').text(data["clinicians"])
    $('.forms').text(data["forms"])
    $('.forms-completed').text(data["complete"])
    $('.severe').text(data["severe"])
    $('.eligible').text(data["eligible"])
    $('.reassessed').text(data["reassessed"])
}

function sortData(classId, column, patients){
    $(classId).change(function() {
            $.ajaxSetup({
                headers: {
                    "X-CSRFToken": document.querySelector('[name=csrfmiddlewaretoken]').value,
                }
            });

            let val = $(this).val()
            if (val === "severe"){
                val = "Severe Pneumonia OR very Severe Disease"
                column = "diagnosis_1"
            }
            else if (val === "pneumonia"){
                val = "Pneumonia"
                column = "diagnosis_7"
            }
            else if (val === "no signs"){
                val = "No signs of Pneumonia or Wheezing illness"
                column = "diagnosis_3"
            }
            else if (val === "cold"){
                val = "Cough/Cold/No Pneumonia"
                column = "diagnosis_7"
            }

            let data_BlobX = new Blob( [JSON.stringify(patients)], {type: 'text/json;charset=utf-8'})

            let formData = new FormData();
            formData.append('health', val)
            formData.append('data', data_BlobX)
            formData.append('name', column)
            formData.append('action', 'health')

            $.ajax({
                method: 'POST',
                url: "/",
                data: formData,
                processData: false,
                contentType: false,
                success: function(resp){
                    $(".patient tr").remove()
                    patients = resp.data
                    fillTable(patients)
                },
                error: function (error){
                    console.log(error)
                }

            });
        })
}