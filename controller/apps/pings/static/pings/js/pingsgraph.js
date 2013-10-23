function pingsgraph(url) {
    $.getJSON(url, function(data) {
        // Create a timer
        var start = + new Date();
        // split the data set intopacket loss and rtt
        var loss = [],
            rtt = [],
            rtt_avg = [],
            dataLength = data.length;
        for (i = 0; i < dataLength; i++) {
            rtt.push([
                data[i][0], // the date
                data[i][3], // high
                data[i][4] // low
            ]);
            rtt_avg.push([
                data[i][0], // the date
                data[i][2] // avg
            ])
            loss.push([
                data[i][0], // the date
                data[i][1] // the rtt
            ])
        }
        // create the chart
        $('#pingchart').highcharts('StockChart', {
            chart: {
                events: {
                    load: function(chart) {
                        this.setTitle(null, {
                            text: 'Built chart at '+ (new Date() - start) +'ms'
                        });
                    }
                },
                zoomType: 'x'
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
                selected: 2
            },
        yAxis: [{ // Primary yAxis
            title: {
                text: 'Packet Loss',
                style: {
                    color: '#ef2929'
                }
            },
            labels: {
                formatter: function() {
                    return this.value + '%';
                },
                style: {
                    color: '#4572A7'
                }
            },
            opposite: true,
            min: 0,
            max: 100
        }, { // Secondary yAxis
            labels: {
                formatter: function() {
                    return this.value + 'ms';
                },
                style: {
                    color: '#4572A7'
                }
            },
            title: {
                text: 'RTT',
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
        navigator: {
            baseSeries: 2,
        },
        series: [{
                type: 'line',
                color: '#ef2929',
                name: 'loss',
                data: loss
       }, {
                type: 'areasplinerange',
                color: '#8ae234',
                name: 'rtt range',
                data: rtt,
                yAxis: 1
        }, {
                type: 'line',
                color: '#4e9a06',
                name: 'rtt',
                data: rtt_avg,
                yAxis: 1
        }]
        });
    });
};
