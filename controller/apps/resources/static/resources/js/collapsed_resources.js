(function($) {
    $(document).ready(function() {
        var id = 'resources';
        var selector = "h2:contains('Resources')";
        
        if ($(selector).parent().find("ul.errorlist").length == 0){
            $(selector).parent().addClass("collapsed");
            $(selector).append(" (<a class=\"collapse-toggle\" id=\""+id+"collapser\" href=\"#\">Show</a>)");
            $("#"+id+"collapser").click(function(e) {
                $(selector).parent().toggleClass("collapsed");
                if ($(selector).children().text() == 'Show') {
                    $(selector).children().text('Hide');
                } else {
                    $(selector).children().text('Show');
                }
                e.preventDefault();
            });
        };
    });
})(django.jQuery);


