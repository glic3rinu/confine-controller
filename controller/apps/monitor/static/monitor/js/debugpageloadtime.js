function debugpageloadtime(url, tag) {
    $.getJSON(url, function(data) {
        // Create a timer
        var start = + new Date();
        // split the data set intopacket loss and rtt
        var elapsed = [],
            user = [],
            system = [],
            queries = [],
            dataLength = data.length;
        for (i = 0; i < dataLength; i++) {
            elapsed.push([
                data[i][0], // the date
                data[i][1]['elapsed'], // high
            ]);
            user.push([
                data[i][0], // the date
                data[i][1]['user'], // high
            ]);
            system.push([
                data[i][0], // the date
                data[i][1]['system'] // avg
            ]);
            queries.push([
                data[i][0], // the date
                data[i][1]['queries'] // avg
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
                alignTicks: false
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
                selected: 1
            },
        yAxis: [{ // Primary yAxis
            labels: {
                formatter: function() {
                    return this.value + ' ms';
                },
                style: {
                    color: '#4572A7'
                },
            },
            title: {
                text: 'Load Time',
                style: {
                    color: '#4e9a06'
                }
            },
            min: 0
        }],
        tooltip: {
            color: 'blue',
            shared: true
        },
        scrollbar : {
            enabled : false
        },
        series: [{
                type: 'line',
                name: 'Elapsed',
                data: elapsed,
        }, {
                type: 'line',
                name: 'User',
                data: user,
        }, {
                type: 'line',
                name: 'System',
                data: system,
        }, {
                type: 'line',
                name: 'Queries',
                data: queries,
        }]
        });
    });
};
