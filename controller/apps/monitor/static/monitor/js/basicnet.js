function basicnet(url, tag) {
    $.getJSON(url, function(data) {
        // Create a timer
        var start = + new Date();
        // split the data set intopacket loss and rtt
        var tx = [],
            rx = [],
            dataLength = data.length;
        for (i = 0; i < dataLength; i++) {
            tx.push([
                data[i][0], // the date
                0,
                data[i][1]['current-TX'], // high
            ]);
            rx.push([
                data[i][0], // the date
                data[i][1]['current-TX'],
                data[i][1]['current-TX']+data[i][1]['current-RX'] // avg
            ])
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
                selected: 1
            },
        yAxis: [{
            title: {
                text: 'Bytes per second',
            },
            min: 0,
        }],
        tooltip: {
            color: 'blue',
            shared: true,
            formatter: function() {
                var s = '<span style="font-size:10px;">'+Highcharts.dateFormat('%A, %b %e, %H:%M', this.x)+'</span>';
                $.each(this.points, function(i, point) {
                    s += '<br/><span style="color:'+point.series.color+';">'+ point.series.name +'</span>: <b>'+
                        humanFileSize((point.point.high-point.point.low).toFixed(2))+'/s</b>';
                });
                
                return s;
            },
        },
        scrollbar : {
            enabled : false
        },
        navigator: {
            baseSeries: 1,
        },
        series: [{
                step: true,
                name: 'RX',
                data: rx,
        }, {
                step: true,
                name: 'TX',
                data: tx,
        }]
        });
    });
};
