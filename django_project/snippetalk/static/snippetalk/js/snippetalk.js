var old_tab;
var old;
var height;
var mine;
var data_source;
var parent_comment;


$.ajaxSetup({
  headers: {
    'X-CSRFToken': $("input[name=csrfmiddlewaretoken]").val()
  }
});


var commentForm =
  $('<div class="row" style="padding-left: 40px">' +
    '<div class="col-xs-7 col-sm-7 col-md-7 col-lg-7 comment-form">' +
    '<textarea id="comment" class="form-control" rows="3" placeholder="Enter comment"></textarea>' +
    '<div class="row tools">' +
    'Snippets: <ul id="snippets"><ul>' +
    '</div>' +
    '<div class="row tools">' +
    '<div class="btn-group" role="group" id="comment-buttons" style="float: right">' +
    '<button class="btn btn-danger" id="cancel-comment" onclick="closeCommentForm()" >' +
    '<span class="glyphicon glyphicon-remove" aria-hidden="true"></span>&nbsp;&nbsp;Cancel' +
    '</button>' +
    '<button class="btn btn-success" id="add-comment" onclick="postComment()">' +
    'Add Comment&nbsp;&nbsp;<span class="glyphicon glyphicon-share-alt" aria-hidden="true"></span>' +
    '</button>' +
    '</div>' +
    '<ul class="nav nav-pills">' +
    '<li role="presentation">' +
    '<button class="btn btn-default round" data-toggle="modal" href="#existing-modal" role="button" aria-haspopup="true" aria-expanded="false">'+
    '<span class="glyphicon glyphicon-paperclip"></span>' +
    '</button>' +
    '</li>' +
    '</ul>' +
    '</div>' +
    '</div>'+
    '</div>');


var commentSnippets = [];


var opts = {
  lines: 13 // The number of lines to draw
  , length: 10 // The length of each line
  , width: 4 // The line thickness
  , radius: 10 // The radius of the inner circle
  , scale: 0.5 // Scales overall size of the spinner
  , corners: 1 // Corner roundness (0..1)
  , color: '#999999' // #rgb or #rrggbb or array of colors
  , opacity: 0.25 // Opacity of the lines
  , rotate: 0 // The rotation offset
  , direction: 1 // 1: clockwise, -1: counterclockwise
  , speed: 1 // Rounds per second
  , trail: 60 // Afterglow percentage
  , fps: 20 // Frames per second when using setTimeout() as a fallback for CSS
  , zIndex: 2e9 // The z-index (defaults to 2000000000)
  , className: 'spinner' // The CSS class to assign to the spinner
  , top: '30px' // Top position relative to parent
  , left: '50%' // Left position relative to parent
  , shadow: false // Whether to render a shadow
  , hwaccel: false // Whether to use hardware acceleration
  , position: 'relative' // Element positioning
};


function showAlert(message, type){
  $.notify(message, {
    animate: {
      enter: 'animated bounceIn',
      exit: 'animated bounceOut'
    },
    type: type
  });
}


function closeCommentForm(){
  commentForm.remove();
}


function replaceCode(data, status, xhr){
  $('.highlight ol').html(data.code);
  $('#code-shadow').hide();
  $('#raw').find('textarea').height($('#highlight').height());
  $('#desc').find('textarea').height($('#highlight').height());
}


function updateCode(code, l){
 $('#code-shadow').show();
  var opt = {
    url: '/snippetalk/highlight',
    type: 'get',
    data: {lang: l, code: code},
    success: replaceCode,
    complete: $('#code-shadow').hide
  };
  $.ajax(opt);
}


function saved(data, status, xhr){
  if(data.link){
    window.location.replace(data.link);
  } else {
    if(data.mod_time){
      $('#modified').text(data.mod_time);
    }
    $('.editable-unsaved').removeClass('editable-unsaved');
    //showAlert('tr', {text: 'Snipped saved'}, 'successgloss', true, 5000);
    showAlert('Snipped Saved.', 'success');
  }
}


function notSaved(xhr, message, kk){
  //showAlert('tr', { text: "Can' save snippet"}, 'errorgloss', false, 0);
  showAlert("Can't save snippet.", 'danger');
}


function saveSnippet(){
  if($('#raw-ta').val().trim()) {
    var data = {
      'id': $('#snippet-id').val(),
      'name': $('#name').editable('getValue', true),
      'public': $('#public').editable('getValue', true),
      'language': $('#lang').editable('getValue', true),
      'code': $('#raw-ta').val().trim(),
      'description': $('#desc-ta').val()
    };
    var opt = {
      url: '/snippetalk/save/',
      type: 'post',
      data: data,
      success: saved,
      error: notSaved
    };
    $.ajax(opt);
  } else showAlert('tr', { text: 'Snippet can\'t be empty, please fill "Raw" tab'}, 'errorgloss', false, 0);
}


function insertComment(data, status, xhr){
  var parent = $('#answers-' + data.parent_id);
  parent.append(data.html);
  $('#comment-count').text(data.comment_count);
  closeCommentForm();
  //showAlert('tr', {text: 'Comment added'}, 'successgloss', true, 5000);
  showAlert('Comment Added', 'success');
}


function commentError(xhr, message, kk){
  //showAlert('tr', { text: "Can't save comment"}, 'errorgloss', false, 0);
  showAlert("Can't save comment", 'danger');
}


function postComment(){
  var comment = $('textarea#comment').val().trim();
  if(comment) {
    var data = {
      id: $('#snippet-id').val(),
      parent: parent_comment,
      comment: comment,
      snippets: JSON.stringify(commentSnippets)
    };
    var opt = {
      url: '/snippetalk/comment/',
      type: 'post',
      data: data,
      success: insertComment,
      error: commentError
    };
    $.ajax(opt);
  } else showAlert('tr', { text: 'Comment can\'t be empty.'}, 'errorgloss', false, 0);
  $('textarea#comment').val('');
}


function onUpload(e){
  var data = JSON.parse(e.target.response);
  $('#name').editable('setValue', data.name);
  $('#lang').editable('setValue', data.lang_code);
  $('#raw-ta').val(data.raw);
  $('#raw-ta').text(data.raw);
  $('.highlight ol').html(data.highlighted);
}


function sendFile() {
  if($('#file').val()) {
    var form = document.forms.namedItem("fileform");
    var fData = new FormData(form);
    var oReq = new XMLHttpRequest();
    oReq.open("POST", "/snippetalk/upload/", true);
    oReq.onload = onUpload;
    oReq.send(fData);
  }
}


function replacePreview(data, status, xhr){
  $('#my-snippet ol').html(data.code);
}


function get_snippet_preview() {
  var opt = {
    url: '/snippetalk/preview/',
    type: 'get',
    data: {
      id: $('#snippet-select').val()
    },
    success: replacePreview
  };
  $.ajax(opt);
}


$('document').ready(function(){
  var highlight = $('#highlight');

  $('#raw').find('textarea').height(highlight.height());
  $('#desc').find('textarea').height(highlight.height());

  new Spinner(opts).spin(document.getElementById('code-shadow'));

  $.fn.editable.defaults.mode = 'inline';
  $('#name').editable({disabled : !mine});
  $('#public').editable({
    disabled : !mine,
    source: [{value: 1, text: "Public"}, {value: 2, text: "Private"}]
  });
  var lang = $('#lang');
  lang.editable({disabled : !mine, source: data_source});
  lang.on('hidden', function(e, reason){
    $('.select2-dropdown').hide();
    /*if(lang.editable('getValue', true) != $('.ccc').val()){
        updateCode($('#raw-ta').val(), $('.ccc').val());
    }*/
  });
  lang.on('shown', function(e, editable) {
    $('h2 small button[type="submit"]').click(function(event){
      if(lang.editable('getValue', true) != $('.ccc').val()){
        updateCode($('#raw-ta').val(), $('.ccc').val());
      }
    });
  });

  $('[data-toggle="tooltip"]').tooltip({animation: false});

  $('a[href="#highlight"]').on('shown.bs.tab', function(event){
    if($('#raw-ta').val() != $('#raw-ta-hidden').val()){
      $('#raw-ta-hidden').val($('#raw-ta').val());
      updateCode($('#raw-ta').val(), lang.editable('getValue', true));
    }
  });

  $('#snippet-select').select2({
    width: '200px'
  });

  $('#save').click(saveSnippet);

  $('#add-comment').click(postComment);
  $('textarea#comment').keypress(function(event, elem){
    if((event.ctrlKey) && ((event.keyCode == 0xA)||(event.keyCode == 0xD))){
      postComment();
    }
  });

  $('.expand').click(function(e){
    console.log($(this));
    if($(this).attr('data-original-title') == 'Collapse')
      $(this).attr('data-original-title', 'Expand');
    else
      $(this).attr('data-original-title', 'Collapse');
    $($(this).attr('data-target')).collapse('toggle');
    $(this).children().toggleClass('glyphicon-chevron-down');
    $(this).children().toggleClass('glyphicon-chevron-right');
  });

  $('.answer').click(function(e){
    parent_comment = $(this).attr('data-id');

    var prev = $(this).closest('.list-group-item').next('.list-group')[0];
    //console.log(prev);
    commentForm.insertAfter(prev);
    $('html, body').animate({
      scrollTop: commentForm.offset().top
    }, 500);
  });

  $('#comment').click(function(e){
    parent_comment = null;
    commentForm.insertAfter($('.comments'));
    $('html, body').animate({
      scrollTop: commentForm.offset().top
    }, 500);
  });

  $('#upload').click(function(e){
    $('#file').click();
  });

  $('#file').change(sendFile);

  $('#snippet-select').on('change', get_snippet_preview);

  $('#add-snippet').click(function(e){
    var id = $('#snippet-select').val();
    var name = $('#snippet-select option[value="' + id + '"]').text();
    if($.inArray(id, commentSnippets) == -1) {
      commentSnippets.push(id);
      var rem = $('<a name="remove-snippet" href="#" data-id="' + id + '">&times;</a>');
      var list_item = $('<li>' + name + ' </li>');
      list_item.append(rem);
      list_item.appendTo($('#snippets'));
      rem.click(function (e) {
        e.preventDefault();
        list_item.remove();
        commentSnippets.splice(commentSnippets.indexOf(id), 1);
      });
    }
  });

  $('[data-toggle="tooltip"]').mouseleave(function(e){
    $(this).tooltip('hide');
  });
});