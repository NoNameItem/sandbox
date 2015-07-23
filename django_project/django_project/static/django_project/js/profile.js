/**
 * Created by nonameitem on 09.07.15.
 */

var file_selected = false;
var userId;


$("#id_image").bind('change', function(event){
    file_selected = true;
    $(".form-select").submit();
});


$(".form-select").bind('submit', function(event){
    if(!file_selected) {
        event.preventDefault();
        $("#id_image").click();
    }
});


$('#new-chat-submit').bind('click', function(event){
    $('#new-chat-form').submit();
})