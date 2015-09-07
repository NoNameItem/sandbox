/**
 * Created by nonameitem on 06.09.15.
 */
function showAlert(pos, message, type, fadeOutEnable, fadeOutDelay){
  $('#' + pos + '-notify').notify({
      message: message,
      type: type,
      fadeOut: {enabled: fadeOutEnable, delay: fadeOutDelay}
    }).show();
}