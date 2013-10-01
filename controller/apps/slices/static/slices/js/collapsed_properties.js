(function($) {
    $(document).ready(function() {
        var selector = "h2:contains('properties')";
        $(selector).parent().addClass("collapsed");
        $(selector).append(" (<a class=\"collapse-toggle\" id=\"customcollapser\" href=\"#\">Show</a>)");
        $("#customcollapser").click(function(e) {
            $(selector).parent().toggleClass("collapsed");
            if ($(selector).children().text() == 'Show') {
                $(selector).children().text('Hide');
            } else {
                $(selector).children().text('Show');
            }
            e.preventDefault();
        });
    });
})(django.jQuery);


