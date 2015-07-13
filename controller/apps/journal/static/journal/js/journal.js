$(document).ready(function() {
    // load sliver details via AJAX
    $('.sliver .info a').on("click", function() {
        url = $(this).data('sliver-url');
        $('#sliver-detail-content').load(url);
    });
});
