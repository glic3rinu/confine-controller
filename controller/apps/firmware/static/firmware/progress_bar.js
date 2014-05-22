function progress_bar(url) {
    $("#description").html('Waiting for your task to begin...');
    $("#progressbar").progressbar({ value: 0 });
    var freq = 1000, last = 1, current = 0, warning_counter = 0;
    function update_progress_info() {
        $.getJSON(url, function (data, status) {
            if (data) {
                console.log(data);
                if (data.progress == last && data.next > current) {
                    current++;
                    warning_counter = 0; // reset counter, it's progressing
                } else {
                    current = data.progress;
                    warning_counter++;
                }
                // Show a warning, build seems hanged.
                if (warning_counter == 5) {
                    console.log("Seems that something goes wrong!");
                    $("#firmware-warning").show();
                }
                last = data.progress;
                $("#progressbar").progressbar({ value: current });
                $("#description").html(data.description);
                $("#content_message").html(data.content_message);
                if (data.state != 'PROCESS') {
                    window.location = window.location.href;
                    return true;
                }
            }
            window.setTimeout(update_progress_info, freq);
        })
        .error(function (data, status) {
            window.location = window.location.href;
            return true;
        });
    }
    window.setTimeout(update_progress_info, freq);
}
