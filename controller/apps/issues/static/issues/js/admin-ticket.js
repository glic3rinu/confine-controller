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
        
        $('#load-preview').click(function() {
            var data = { 
                'data': $('#id_messages-2-0-content').val(),
                'csrfmiddlewaretoken': $('[name=csrfmiddlewaretoken]', '#ticket_form').val(),
            }
            $('#content-preview').load("/admin/issues/ticket/preview/", data);
            return false;
        });
    });
})(django.jQuery);
