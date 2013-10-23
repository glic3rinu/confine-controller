(function($) {
    $(document).ready(function($) { 
        // check if exists TOTAL report and apply special class
        $th_last = $('#result_list tr:last th');
        if ($th_last.html().search("(None)") != -1) {
            $('#result_list tr:last').addClass('last-child');
            $th_last.empty().append("TOTAL");
        }
        
        // add extraheader
        $('#result_list thead').prepend('<tr><th class="empty"></th><th colspan="4">Nodes</th><th class="empty"></th><th colspan="4">Sliver</th></tr>');

        //TODO: replace JS for overrided template?
    });
})(django.jQuery);
