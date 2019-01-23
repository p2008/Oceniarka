$(function(){
    coordinator_topics = $("#pdf").attr("data").split('search=')[1].split('&')[0];

    for(let i=0; i<=$("#id_topic").length; i++){
        if(coordinator_topics.indexOf($("#id_topic_" + i).val())){
            $("#id_topic_" + i).attr("disabled", true)
        }
    }

});