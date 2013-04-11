function progress_bar(url) {
    $( "#description" ).html('Waiting for your task to begin ...');
    $( "#progressbar" ).progressbar({ value: 0 });
    var freq = 1000;
    var last = 1;
    var current = 0;
    function update_progress_info() {
        $.getJSON(url, function(data, status){
            if (data) {
                console.log(data);
                if (data.progress == last && data.next > current){
                    current++;
                } else {
                    current = data.progress;
                }
                last = data.progress
                $( "#progressbar" ).progressbar({ value: current });
                $( "#description" ).html(data.description);
                $( "#content_message" ).html(data.content_message);
                if ( data.state != 'PROCESS') {
                    window.location = window.location.href;
                    return true;
                }
            }
            window.setTimeout(update_progress_info, freq);
        })
        .error(function(data, status) { 
            window.location = window.location.href;
            return true;
        });
    };
    window.setTimeout(update_progress_info, freq);
};
