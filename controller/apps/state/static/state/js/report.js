(function($) {
    $(document).ready(function($) { 
        // add hihghlit class for remarking values != 0
        $('#result_list tbody td').each(function() {
            if($(this).text() > 0) {
                $(this).addClass("highlight");
            }
        });
    });
})(jQuery);
