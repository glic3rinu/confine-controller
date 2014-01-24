(function($) {
    $(document).ready(function() {
        var id = 'gis';
        var selector = "#gis-group fieldset.module h2";
        //var selector = "h2:contains('Geolocation')";
        
        if ($(selector).parent().find("ul.errorlist").length == 0){
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
        // HACK: hide map after loading for avoid Openlayers bug #2187
        setTimeout(function() {
            $(selector).parent().addClass("collapsed");
        }, 500);
    });
})(django.jQuery);
