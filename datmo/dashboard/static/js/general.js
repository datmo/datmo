var body = document.body, timer;

window.addEventListener('scroll', function() {
    clearTimeout(timer);
    if(!body.classList.contains('disable-hover')) {
        body.classList.add('disable-hover')
    }

    timer = setTimeout(function(){
        body.classList.remove('disable-hover')
    },500);
}, false);

$(document).ready(function(){
    $('.clone-box').on('click', function(e){
        var target = $(e.target);
        if (target.hasClass('btn') || target[0].nodeName == 'IMG'){
        var parent = $(e.target).parents('.clone-box');
        var address = parent.find('.cli-command');
        copyToClipboard(address.text());
        address.addClass('selected')
        setTimeout(function(){
            address.removeClass('selected');
        }, 600);
        }
    });
    $('.js-confirm').on('click', function(e){
        e.preventDefault();
        if (confirm(e.target.dataset.confirm || 'Are you sure?')){
            $(e.target).parents('form').submit();
        }
    });
    $('.lazy-load-image').each(function(idx, elem){
        elem = $(elem);
        var img = new Image();
        var full_size_img = elem.attr('data-fullsize');
        img.onload = function(){
            elem.attr('src', full_size_img)
        }
        img.src = full_size_img;
    });
})


/*
  From https://stackoverflow.com/questions/400212/how-do-i-copy-to-the-clipboard-in-javascript
*/
function copyToClipboard(text) {
    if (window.clipboardData && window.clipboardData.setData) {
        // IE specific code path to prevent textarea being shown while dialog is visible.
        return clipboardData.setData("Text", text);

    } else if (document.queryCommandSupported && document.queryCommandSupported("copy")) {
        var textarea = document.createElement("textarea");
        textarea.textContent = text;
        textarea.style.position = "fixed";  // Prevent scrolling to bottom of page in MS Edge.
        document.body.appendChild(textarea);
        textarea.select();
        try {
            return document.execCommand("copy");  // Security exception may be thrown by some browsers.
        } catch (ex) {
            console.warn("Copy to clipboard failed.", ex);
            return false;
        } finally {
            document.body.removeChild(textarea);
        }
    }
}