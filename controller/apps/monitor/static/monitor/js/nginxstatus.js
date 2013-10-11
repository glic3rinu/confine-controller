function nginxstatus(url, tag) {
    $.getJSON(url, function(data) {
        // Create a timer
        var start = + new Date();
        // split the data set intopacket loss and rtt
        var requests = [],
            reading = [],
            writing = [],
            waiting = [],
            dataLength = data.length;
        for (i = 0; i < dataLength; i++) {
            rw = data[i][1]['reading']+data[i][1]['writing'];
            requests.push([
                data[i][0],
                data[i][1]['current-handled-requests'],
            ]);
            reading.push([
                data[i][0],
                0,
                data[i][1]['reading'],
            ]);
            writing.push([
                data[i][0],
                data[i][1]['reading'],
                rw,
            ]);
            waiting.push([
                data[i][0],
                rw,
                rw+data[i][1]['waiting'],
            ]);
        }
        // create the chart
        $('#'+tag).highcharts('StockChart', {
            chart: {
                events: {
                    load: function(chart) {
                        this.setTitle(null, {
                            text: 'Built chart at '+ (new Date() - start) +'ms'
                        });
                    }
                },
                zoomType: 'x',
                type: 'arearange'
            },
            credits: {
                enabled: false
            },
            rangeSelector: {
                buttons: [{
                    type: 'day',
                    count: 1,
                    text: '1d'
                }, {
                    type: 'day',
                    count: 3,
                    text: '3d'
                }, {
                    type: 'week',
                    count: 1,
                    text: '1w'
                }, {
                    type: 'month',
                    count: 1,
                    text: '1m'
                }, {
                    type: 'month',
                    count: 6,
                    text: '6m'
                }, {
                    type: 'year',
                    count: 1,
                    text: '1y'
                }, {
                    type: 'all',
                    text: 'All'
                }],
                selected: 3
            },
            yAxis: [{ // Primary yAxis
                title: {
                    text: 'Requests',
                    style: {
                        color: '#ef2929'
                    }
                },
                min: 0,
            }, { // Secondary yAxis
                title: {
                    text: 'Workers',
                    style: {
                        color: '#4e9a06'
                    }
                },
                opposite: true,
                min: 0,
            }],
        tooltip: {
            color: 'blue',
            shared: true
        },
        scrollbar : {
            enabled : false
        },
        series: [{
                name: 'Reading',
                data: reading,
                yAxis: 1
        }, {
                name: 'Writing',
                data: writing,
                yAxis: 1
        }, {
                name: 'Waiting',
                data: waiting,
                yAxis: 1
        }, {
                type: 'line',
                name: 'Handled requests',
                data: requests,
        }]
        });
    });
};
