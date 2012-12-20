var selector = "h2:contains('TITLE_OF_INLINE_BLOCK')";
$(selector).parent().addClass("collapsed");
$(selector).append(" (<a class=\"collapse-toggle\" id=\"customcollapser\" href=\"#\"> Show </a>)");
$("#customcollapser").click(function() {
    $(selector).parent().toggleClass("collapsed");
});

