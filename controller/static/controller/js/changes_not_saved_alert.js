$(document).ready(function () {
    var unsaved = false;
    
    $(":input").change(function(){ //trigers change in all input fields including text type
        unsaved = true;
    });
    
    function unloadPage(){ 
        if(unsaved){
            return "You have unsaved changes on this page. Do you want to leave this page and discard your changes or stay on this page?";
        }
    }
    window.onbeforeunload = unloadPage;
    
    $('input[type=submit]').click(function () {
            window.onbeforeunload = null;
    });
});

