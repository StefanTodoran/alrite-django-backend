$(document).ready(function() {
    if ($('div').is('.content')){
        let data = JSON.parse(document.getElementById('data').textContent)
        fillTable(data)

        $('.hc').change(function() {
            $.ajaxSetup({
                headers: {
                    "X-CSRFToken": document.querySelector('[name=csrfmiddlewaretoken]').value,
                }
            });

            let val = $(this).val()

            let new_data = JSON.stringify(data);

            let formData = new FormData();
            formData.append('healthy', val)
            formData.append('data', new_data)

            $.ajax({
                method: 'POST',
                url: "/",
                data: formData,
                processData: false,
                contentType: false,
                success: function(resp){
                    // $(".weekly tr").remove()
                    let info = resp.data

                },
                error: function (error){
                    console.log(error)
                }

            });
        })
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