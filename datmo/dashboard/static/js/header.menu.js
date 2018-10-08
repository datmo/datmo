$(document).ready(function(){
  $('.product').on('click', function(e){
    var wrapper = $(this).next();
    var parent = wrapper.parent();

    function outsideMenuClick (){
      setTimeout(function(){
        $(document.body).one('click', function(e){
            if (parent.find(e.target).length){
              outsideMenuClick();
            } else {
              wrapper.addClass('hidden');
            }
        });
      }, 100);
    }
    if (wrapper.hasClass('hidden')){
      e.stopPropagation();
      wrapper.removeClass('hidden');
      outsideMenuClick();
    } else {
      wrapper.addClass('hidden');
    }
  })
  
  if (typeof window.nouser === 'undefined'){
    $('.header-user-profile img').on('click', function(e){
      var wrapper = $(this).next();
      var parent = wrapper.parent();

      function outsideMenuClick (){
        setTimeout(function(){
          $(document.body).one('click', function(e){
              if (parent.find(e.target).length){
                outsideMenuClick();
              } else {
                wrapper.addClass('hidden');
              }
          });
        }, 100);
      }
      if (wrapper.hasClass('hidden')){
        e.stopPropagation();
        wrapper.removeClass('hidden');
        outsideMenuClick();
      } else {
        wrapper.addClass('hidden');
      }
    })
  }

  // remove error/success/warning messages when clicked.
  $('.form-message > .message').on('click', function(e){
    e.preventDefault();
    e.stopPropagation();
    $('.form-message').remove();
  });
});

$(document).ready(function() {
    $('.snapshots-detail').on('click', function() {
        $(this).toggleClass('open').siblings().removeClass('open');
    });
    $('.mobile-menu').on('click', function(){
        var x = document.getElementById("myTopnav");
        if (x.className === "topnav") {
            x.className += " responsive";
        } else {
            x.className = "topnav";
        }
    })
});