/**
 * Created by nonameitem on 27.09.15.
 */
var currChatId = null;
var username = null;
var userId;
var reconnect = true;


function newMessage(mess){
  if(mess.sender != username && mess.id != currChatId)
  $.notify({
    title: "<h5>[" + mess.name + "] New Message</h5> ",
    message: '[' + mess.sender + ']:' + mess.text,
    url: mess.link,
    target: "_blank"
  }, {
    delay: 0,
    type: 'warning',
    placement: {
      from: 'bottom',
      align: 'right'
    },
    animate: {
      enter: 'animated fadeInRight',
      exit: 'animated fadeOutRight'
    }
  });
}


function newTopic(mess){
  if(mess.sender != username && mess.id != currChatId)
  $.notify({
    title: "<h5>[" + mess.name + "] New Topic</h5> ",
    message: mess.sender + ' changed topic to "' + mess.text + '"',
    url: mess.link,
    target: "_blank"
  }, {
    delay: 0,
    type: 'warning',
    placement: {
      from: 'bottom',
      align: 'right'
    },
    animate: {
      enter: 'animated fadeInRight',
      exit: 'animated fadeOutRight'
    }
  });
}


function newChat(mess){
  if(mess.sender != username && mess.id != currChatId)
  $.notify({
    title: "<h5>New Chat</h5> ",
    message: mess.sender + ' created new chat <strong>' + mess.name + '(' + mess.text + ')</strong>',
    url: mess.link,
    target: "_blank"
  }, {
    delay: 0,
    type: 'warning',
    placement: {
      from: 'bottom',
      align: 'right'
    },
    animate: {
      enter: 'animated fadeInRight',
      exit: 'animated fadeOutRight'
    }
  });
}


function invited(mess){
  if(mess.sender != username && mess.id != currChatId)
  $.notify({
    title: "<h5>[" + mess.name + "] Invite</h5> ",
    message: mess.sender + ' invited you to chat',
    url: mess.link,
    target: "_blank"
  }, {
    delay: 0,
    type: 'warning',
    placement: {
      from: 'bottom',
      align: 'right'
    },
    animate: {
      enter: 'animated fadeInRight',
      exit: 'animated fadeOutRight'
    }
  });
}


function connect(){
  var ws = new WebSocket(WEBSOCKET_PREFIX + '/notify/' + userId + '/');

  ws.onmessage = function(e){
    var data = JSON.parse(e.data);
    if(data.type == 'M'){
      newMessage(data.mess)
    }
    if(data.type == 'T'){
      newTopic(data.mess)
    }
    if(data.type == 'C'){
      newChat(data.mess)
    }
    if(data.type == 'I'){
      invited(data.mess)
    }
  };

  ws.onerror = function(e){
    reconnect = false;
  };

  ws.onclose = function(e){
    if(reconnect)
      setTimeout(connect, 100);
  };
}


$(document).ready(function(){
  if(username) {
    connect();
  }
});