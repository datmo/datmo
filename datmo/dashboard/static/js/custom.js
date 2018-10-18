// applications
$(document).ready(function() {
    $('.snapshots-detail').on('click', function() {
        $(this).toggleClass('open').siblings().removeClass('open');
    });
});

$(document).ready(function() {
    $('.section-tab ul a').on('click', function() {
        $(this).addClass('active').siblings().removeClass('active');
    });
});

$(document).ready(function() {
    $('.side-nav ul a').on('click', function() {
        $(this).addClass('active').siblings().removeClass('active');
    });
});

$(document).ready(function() {
    $('.section-tab-mobile').on('click', function() {
        $(this).toggleClass('open');
    });
});

$(document).ready(function(){
    if( jQuery(".toggle .title-name").hasClass('active') ){
        jQuery(".toggle .title-name.active").closest('.toggle').find('.toggle-inner').show();
    }
    jQuery(".toggle .title-name").click(function(){
        if( jQuery(this).hasClass('active') ){
            jQuery(this).removeClass("active").closest('.toggle').find('.toggle-inner').slideUp(200);
        }
        else{
            jQuery(this).addClass("active").closest('.toggle').find('.toggle-inner').slideDown(200);
        }
    });
});

