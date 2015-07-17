/**
 * Created by nonameitem on 15.07.15.
 */

SLIDE_SPEED = 'fast';

//alert($('input[type=hidden]').val());

$.ajaxSetup({
    headers: {
        'X-CSRFToken': $('input[name=csrfmiddlewaretoken]').val()
    }
});

var add_user_button = $('#add_user_button');
var add_user_form = $('#add_user_form');
var messageField = $('#id_message');
var chat;

add_user_form.hide();

function scrollDown(){
    var chatWindow = $('.main');
    //var height = chatWindow.height;
    chatWindow.scrollTop(chatWindow.prop("scrollHeight") + 100);

}

function showAddUserForm(){
    add_user_button.slideUp(SLIDE_SPEED);
    add_user_form.slideDown(SLIDE_SPEED);
}

function hideUserForm(){
    $('.selectpicker').selectpicker('deselectAll');
    add_user_form.slideUp(SLIDE_SPEED);
    add_user_button.slideDown(SLIDE_SPEED);
}

add_user_button.bind('click', showAddUserForm);
$('#cancel_add_user').bind('click', hideUserForm);
$(document).ready(function(){
    $.fn.editable.defaults.mode = 'inline';
    $('#topic').editable();
    scrollDown();
});

add_user_form.bind('submit', function(event){
    event.preventDefault();
    var opt = {
        'url': '/chat/add_users/' + chat + '/',
        'type': 'post',
        'data': {'selected': JSON.stringify($('.selectpicker').val())}
    };
    if(opt.data.selected != 'null') {
        $.ajax(opt);
        hideUserForm();
    }
});

function getMessageBlock(self, message){
    var block = $(
        '<div class="row message_block">' +
            '<div class="col-xs-2 col-sm-2 col-md-2 col-lg-2" align="right">' +
                '<a href="/user/' + message.username + '" target="_blank" class="thumbnail">' +
                    '<img src="' + message.photo + '" alt="Image">' +
                '</a>' +
            '</div>' +
        '</div>'
        );
    var textBlock = $('<div class="col-xs-9 col-sm-9 col-md-9 col-lg-9"></div>');
    var messages = $(
        '<div class="alert">' +
            '<a href="/user/' + message.username + '" target="_blank" class="sender"><strong>' + message.username + '</strong></a>' +
            '<div>' + message.message + '</div>' +
        '</div'
    );
    messages.addClass(self ? 'alert-success' : 'alert-info');
    messages.appendTo(textBlock);
    textBlock.appendTo(block);
    return block;
}

function populateUsers(users){
    var userList = $('#id_userlist');
    userList.find('> li').remove();
    for(var i=0; i<users.length; i++){
        $('<li><p><a href="/user/' + users[i] + '" target="_blank">' + users[i] + '</a></p></li>').appendTo(userList);
    }
}

function populatePotentialUsers(users){
    var selector = $('.selectpicker');
    selector.find('> option').remove();
    for(var i = 0; i<users.length; i++){
        $('<option value="' + users[i][0] + '">' + users[i][1] + '</option>').appendTo(selector);
    }
    selector.selectpicker('refresh');
}

function startChat(chatId, username){
    chat = chatId;
    var ws = new WebSocket('ws://localhost:8889/chat/' + chatId + '/');
    ws.onmessage = function(event){
        var mess = JSON.parse(event.data);
        if(mess.type == 'M'){
            if(mess.username == $('.sender').last().text()){
                $('<div>' + mess.message + '</div>').appendTo($('.alert').last());
            } else {
                var newBlock = getMessageBlock(mess.username == username, mess);
                newBlock.appendTo($('.main'));
            }
            scrollDown();
        } else if(mess.type == 'U'){
            populateUsers(mess.participants);
            //alert(mess.potential_particicpants);
            populatePotentialUsers(mess.potential_participants);
        }
    };

    ws.onclose(function(){
       setTimeout(function() {startChat(chatId, username)}, 100);
    });

    function sendMessage() {
        var opt = {
            'url': '/chat/post/' + chatId + '/',
            'type': 'post',
            'data': {'message': messageField.val()}
        };
        $.ajax(opt);
        messageField.val('');
    }

    $('.send-button').click(sendMessage);

    messageField.keydown(function(event){
        if(event.keyCode == 13) {
            sendMessage()
        }
    })

}