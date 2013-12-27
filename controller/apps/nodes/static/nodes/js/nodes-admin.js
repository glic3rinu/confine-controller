(function($) {
    $(document).ready(function($) {        
        // warn twice user when set_state is set to failure
        $('#id_set_state').on("change", function() {
            if(warn_failure_chosen() == false) {
                $(this).val("safe");
            }
        });
        $('#node_form').on("submit", function() {
            return warn_failure_chosen();
        });
        // add search placeholder. FIXME: generate based on admin search_fields
        $('#searchbar').attr("placeholder", "search by name, description, IP address...")
    });
    /** Show a confirm box to verify the action **/
    function warn_failure_chosen() {
        $set_state = $('#id_set_state');
        if($set_state.val() == "failure") {
            var msg = "Warning! Are you sure do you want to set node " +
                "state to 'FAILURE'? Manual intervention will be required!";
            return confirm(msg);
        }        
    }
})(django.jQuery);
