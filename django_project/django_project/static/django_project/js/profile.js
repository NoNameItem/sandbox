/**
 * Created by nonameitem on 09.07.15.
 */

$.ajaxSetup({
  headers: {
    'X-CSRFToken': $("input[name=csrfmiddlewaretoken]").val()
  }
});

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
});

$('.add-to-chat').click(function(event){
  var opt = {
    url: '/chat/add_user/' + $(this).attr('data-id') + '/',
    type: 'post',
    data: {user_id: userId},
    success: function(data, status, xhr){
      showAlert('tr', {text: 'User invited to chat ' + $(this).text()}, 'successgloss', true, 5000);
      if($('.add-to-chat').size() == 1){
        $('#invite-button').remove();
        $('#private-chat').css('border-bottom-left-radius', '20px');
        $('#private-chat').css('border-bottom-right-radius', '20px');
      }
      $(this).remove();
    },
    error: function(){
      showAlert('tr', {text: 'Can\'t invite user to chat. Please try again later'}, 'errorgloss', true, 5000);
    }

  };
  $.ajax(opt);
});