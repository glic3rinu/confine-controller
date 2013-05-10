// visibility helper show on hover

(function($) {
    $(document).ready(function($) {
        $v = $('#id_visibility');
        $v_help = $('#ticket_form .field-box.field-visibility .help')
        $v.hover(
            function() { $v_help.show(); }, 
            function() { $v_help.hide(); }
        );
        
        $('#subject-edit').click(function() { 
            $('.field-box.field-subject').show();
        });
    });
})(django.jQuery);
