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
                selected: 1
            },
        tooltip: {
            color: 'blue',
            shared: true,
            formatter: function() {
                var s = '<span style="font-size:10px;">'+Highcharts.dateFormat('%A, %b %e, %H:%M', this.x)+'</span>';
                $.each(this.points, function(i, point) {
                    s += '<br/><span style="color:'+point.series.color+';">'+ point.series.name +'</span>: <b>';
                    if (point.series.name != 'Total')
                        s += humanFileSize((point.point.high-point.point.low))+'</b>';
                    else
                        s += humanFileSize(point.y)+'</b>';
                });
                
                return s;
            },
        },
        yAxis: [{
            title: {
                text: 'Bytes',
            },
            min: 0,
        }],
        scrollbar : {
            enabled : false
        },
        navigator: {
            baseSeries: 2,
        },
        colors: [
           '#f28f43', // bright brown/orage
           '#0d233a', // darkblue
           '#2f7ed8', // skyblue
           '#8bbc21', // bright green
           '#910000', // darkred
           
           '#1aadce', // turkey
           '#492970', // purple
           '#77a1e5', // bright blue
           '#c42525', // red
           '#a6c96a', // greene
        ],
        series: [{
                type: 'line',
                name: 'Total',
                data: total,
        }, {
                name: 'Shared',
                data: shared,
        }, {
                name: 'Buffers',
                data: buffers,
        }, {
                name: 'Cached',
                data: cached,
        }, {
                name: 'Used',
                data: used,
        }]
        });
    });
};
