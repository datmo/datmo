$(document).ready(function(){
  var toggle = {};
  $('.snapshot-diff .load-diff button').on('click', function(e){
    e.preventDefault();
    console.log(e.target);
    console.log(e.target.dataset.file);
    e.target.setAttribute('disabled','disabled');
    e.target.innerHTML = 'loading...';
    $.ajax({
      url: window.location + '/file/' + e.target.dataset.file,
      method: 'GET',
      json: true,
      success: function(body){
          console.log(body.diff);
          $(e.target).parents('.row').addClass('show-diff-placeholder').removeClass('load-diff');
          $(e.target).parents('.row').find('code').html(body.diff);
      }
    })
  });
});