var old_tab;
var old;
var height;
var mine;
var data_source;

$.ajaxSetup({
  headers: {
    'X-CSRFToken': $("input[name=csrfmiddlewaretoken]").val()
  }
});

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

function switch_tab(new_tab, new_body){
  old_tab.removeClass("active");
  old.collapse("hide");
  old_tab = new_tab;
  old = new_body;
  new_tab.addClass('active');
  new_body.collapse('show');
}

function replaceCode(data, status, xhr){
  $('.highlight ol').html(data.code);
  $('#code-shadow').hide();
  $('#raw').find('textarea').height($('.highlight').height());
  $('#desc').find('textarea').height($('.highlight').height());
}

function updateCode(code, l){
  $('#code-shadow').show();
  opt = {
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
    $('.editable-unsaved').removeClass('editable-unsaved');
    $('#tr-notify').notify({
      message: {text: 'Snipped saved'},
      type: 'successgloss',
      fadeOut: {enabled: true, delay: 5000}
    }).show();
  }
}

function notSaved(xhr, message, kk){
  $('#tr-notify').notify({
    message: { text: "Can' save snippet"},
    type: 'errorgloss',
    fadeOut:{enabled: false, delay: 5000}}).show();
}

function saveSnippet(){
  if($('#raw-ta').val()) {
    data = {
      'id': $('#snippet-id').val(),
      'name': $('#name').editable('getValue', true),
      'public': $('#public').editable('getValue', true),
      'language': $('#lang').editable('getValue', true),
      'code': $('#raw-ta').val(),
      'description': $('#desc-ta').val()
    };
    opt = {
      url: '/snippetalk/save/',
      type: 'post',
      data: data,
      success: saved,
      error: notSaved
    };
    $.ajax(opt);
  } else $('#tr-notify').notify({
    message: { text: 'Snippet can\'t be empty, please fill "Raw" tab'},
    type: 'errorgloss',
    fadeOut:{enabled: false, delay: 3000}}).show();

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
  });
  lang.on('shown', function(e, editable) {
    $('h1 small button[type="submit"]').click(function(event){
      if(lang.editable('getValue', true) != $('.ccc').val()){
        updateCode($('#raw-ta').val(), $('.ccc').val());
      }
    });
  });

  $('a[href="#highlight"]').on('shown.bs.tab', function(event){
    if($('#raw-ta').val() != $('#raw-ta-hidden').val()){
      $('#raw-ta-hidden').val($('#raw-ta').val());
      updateCode($('#raw-ta').val(), lang.editable('getValue', true));
    }
  });

  $('#save').click(saveSnippet)
});