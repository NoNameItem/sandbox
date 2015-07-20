/**
 * Created by nonameitem on 15.07.15.
 */

SLIDE_SPEED = 'fast';


$.ajaxSetup({
    headers: {
        'X-CSRFToken': $('input[name=csrfmiddlewaretoken]').val()
    }
});


var add_user_button = $('#add_user_button');
var add_user_form = $('#add_user_form');
var messageField = $('#id_message');
var chat;
var oldest;
var l;
var usrname;


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


function getMessageBlock(self, sender, photo, text){
    var block = $(
        '<div class="row message_block">' +
            '<div class="col-xs-2 col-sm-2 col-md-2 col-lg-2" align="right">' +
                '<a href="/user/' + sender + '" target="_blank" class="thumbnail">' +
                    '<img src="' + photo + '" alt="Image">' +
                '</a>' +
            '</div>' +
        '</div>'
        );
    var textBlock = $('<div class="col-xs-10 col-sm-10 col-md-10 col-lg-10"></div>');
    var messages = $(
        '<div class="alert">' +
            '<a href="/user/' + sender + '" target="_blank" class="sender"><strong>' + sender + '</strong></a>' +
            '<div>' + text + '</div>' +
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


function insertToBeginning(data, status, xhr){
    if(!data.not_all){
        $('.load-more').remove();
    }

    oldest = data.oldest_datetime;

    var chatWindow = $('.main');
    var prevHeight = chatWindow.prop('scrollHeight');

    var first_block = $('.message_block').first();
    var first_sender = $('.sender').first().text();
    for(var i = data.message_blocks.length - 1; i >= 0; i--){
        var message_block = data.message_blocks[i];
        var messages = message_block.messages;
        if(message_block.sender == first_sender){
            for(var j = messages.length - 1; j >= 0; j--){
                $('<div>' + messages[j] + '</div>').insertAfter($('.sender').first());
            }
        } else {
            var new_block = getMessageBlock(message_block.sender == usrname, message_block.sender,
                message_block.photo, message_block.messages[0]);
            for(var j = 1; j < messages.length; j++){
                $('<div>' + messages[j] + '</div>').appendTo(new_block.find('.alert'));
            }
            new_block.insertBefore(first_block);
            first_block = new_block;
            first_sender = first_block.find('a').first().text();
        }
    }
    chatWindow.scrollTop(chatWindow.prop('scrollHeight') - prevHeight);
}

function getPrevious(){
    var opt = {
        'url': '/chat/get_previous/' + chat + '/',
        'type': 'get',
        'data': {'oldest': oldest},
        'success': insertToBeginning,
        'complete': l.stop
    };
    $.ajax(opt);
}


function startChat(chatId, username){
    chat = chatId;
    usrname = username;
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
        } else if(mess.type =='T'){
            $('#topic').text(mess.topic);
        }
    };

    ws.onclose = function(){
       setTimeout(function() {startChat(chatId, username)}, 100);
    };

    function sendMessage() {
        var opt = {
            'url': '/chat/post/' + chatId + '/',
            'type': 'post',
            'data': {'message': messageField.val()}
        };
        if(opt.data.message.length > 0) {
            $.ajax(opt);
            messageField.val('');
        }
    }

    $('.send-button').click(sendMessage);

    messageField.keydown(function(event){
        if(event.keyCode == 13) {
            sendMessage()
        }
    })

}


add_user_button.bind('click', showAddUserForm);

$('#cancel_add_user').bind('click', hideUserForm);

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

$('.load-more').bind('click', function(event){
    l = Ladda.create(this);
    l.start();
    setTimeout(getPrevious, 1000);
});

$(document).ready(function(){
    $.fn.editable.defaults.mode = 'inline';
    $('#topic').editable();
    scrollDown();
});