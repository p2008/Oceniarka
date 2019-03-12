$(function(){
    coordinator_topics = $("#pdf").attr("data").split('search=')[1].split('&')[0];
    //
    // for(let i=0; i<=$("div.form-check").length; i++){
    //     if(coordinator_topics.indexOf($("#id_topic_" + i).val()) === -1){
    //         $("#id_topic_" + i).attr("disabled", true)
    //     }
    // }
$("input:checkbox").each(function() {

	if(coordinator_topics.indexOf($(this).val()) === -1){
            $(this).attr("disabled", true)
        }
})
});

// $(document).ready( function(){
//     $("#search2").keypress(function(){
//         console.log($("#search2").val(), 'sdfds');
//         var control_number =$("#search2").val();
//         $.ajax({
//             type: "GET",
//             url: "/oceniarka/widoklista/",
//             data: {'control_number': control_number},
//             success: function(data) {
//                 console.log("SUCCESS");
//                 $("#searchList").html(data);
//             },
//         });
//     });
//
//     $("#searchList").on("select", "li" , function() {
//         console.log('tralalala');
//         $("#searchform").submit()
//     })
// });
