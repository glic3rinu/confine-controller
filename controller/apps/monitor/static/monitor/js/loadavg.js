function loadavg(url, tag) {
    $.getJSON(url, function(data) {
        // Create a timer
        var start = + new Date();
        // split the data set intopacket loss and rtt
        var one_min = [],
            five_min = [],
            fiveteen_min = [],
            dataLength = data.length;
        for (i = 0; i < dataLength; i++) {
            max5 = data[i][1]['1min']+data[i][1]['5min'];
            one_min.push([
                data[i][0], // the date
                0,
                data[i][1]['1min'], // high
            ]);
            five_min.push([
                data[i][0], // the date
                data[i][1]['1min'],
                max5, // high
            ]);
            fiveteen_min.push([
                data[i][0], // the date
                max5,
                max5+data[i][1]['15min'] // avg
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
        yAxis: [{ // Primary yAxis
            title: {
                text: 'Load'
            },
            min: 0,
        }],
        navigator: {
            baseSeries: 2,
        },
        tooltip: {
            color: 'blue',
            shared: true,
            formatter: function() {
                var s = '<span style="font-size:10px;">'+Highcharts.dateFormat('%A, %b %e, %H:%M', this.x)+'</span>';
                $.each(this.points, function(i, point) {
                    s += '<br/><span style="color:'+point.series.color+';">'+ point.series.name +'</span>: <b>'+
                        (point.point.high-point.point.low).toFixed(2)+'</b>';
                });
                
                return s;
            },
        },
        scrollbar : {
            enabled : false
        },
        series: [{
                name: '15min',
                data: fiveteen_min,
        }, {
                name: '5min',
                data: five_min,
        }, {
                name: '1min',
                data: one_min,
        }]
        });
    });
};
