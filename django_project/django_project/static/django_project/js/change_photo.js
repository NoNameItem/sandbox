/**
 * Created by nonameitem on 09.07.15.
 */

var file_selected = false;

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