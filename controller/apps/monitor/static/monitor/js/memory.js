function memory(url, tag) {
    $.getJSON(url, function(data) {
        // Create a timer
        var start = + new Date();
        // split the data set intopacket loss and rtt
        var used = [],
            buffers = [],
            cached = [],
            shared = [],
            total = [],
            dataLength = data.length;
        for (i = 0; i < dataLength; i++) {
            max_cached = data[i][1]['real-used']+data[i][1]['cached'];
            max_buffers = max_cached+data[i][1]['buffers'];
            used.push([
                data[i][0],
                0,
                data[i][1]['real-used'],
            ]);
            cached.push([
                data[i][0],
                data[i][1]['real-used'],
                max_cached,
            ]);
            buffers.push([
                data[i][0],
                max_cached,
                max_buffers,
            ]);
            shared.push([
                data[i][0],
                max_buffers,
                max_buffers+data[i][1]['shared'],
            ]);
            total.push([
                data[i][0],
                data[i][1]['total'],
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
                alignTicks: false,
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
            labels: {
                formatter: function() {
                    return this.value + ' KBytes';
                },
                style: {
                    color: '#4572A7'
                }
            },
            title: {
                text: 'Bytes',
                style: {
                    color: '#4e9a06'
                }
            }
        }],
        tooltip: {
            color: 'blue',
            shared: true
        },
        scrollbar : {
            enabled : false
        },
        series: [{
                name: 'Used',
                data: used,
        }, {
                name: 'Buffers',
                data: buffers,
        }, {
                name: 'Cached',
                data: cached,
        }, {
                name: 'Shared',
                data: shared,
        }, {
                type: 'line',
                name: 'Total',
                data: total,
        }]
        });
    });
};
