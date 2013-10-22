function webserverstatus(url, tag) {
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
                selected: 1
            },
            yAxis: [{ // Primary yAxis
                title: {
                    text: 'Requests per second',
                },
                min: 0,
            }, { // Secondary yAxis
                title: {
                    text: 'Workers',
                },
                opposite: true,
                min: 0,
            }],
        tooltip: {
            color: 'blue',
            shared: true,
            formatter: function() {
                var s = '<span style="font-size:10px;">'+Highcharts.dateFormat('%A, %b %e, %H:%M', this.x)+'</span>';
                $.each(this.points, function(i, point) {
                    s += '<br/><span style="color:'+point.series.color+';">'+ point.series.name +'</span>: <b>';
                    if (point.series.name != 'Handled requests')
                        s += (point.point.high-point.point.low)+'</b>';
                    else
                        s += point.y.toFixed(3)+' r/s</b>';
                });
                
                return s;
            },
        },
        scrollbar : {
            enabled : false
        },
        navigator: {
            baseSeries: 2,
        },
        colors: [
           '#8bbc21', // bright green
           '#505c6f', // darkblue
           '#2f7ed8', // skyblue
           '#910000', // darkred
           
           '#492970', // purple
           '#8bbc21', // bright green
           '#1aadce', // turkey
           '#f28f43', // bright brown/orage
           '#77a1e5', // bright blue
           '#c42525', // red
           '#a6c96a', // greene
        ],
        series: [{
                name: 'Waiting',
                data: waiting,
                yAxis: 1
        }, {
                name: 'Writing',
                data: writing,
                yAxis: 1
        }, {
                name: 'Reading',
                data: reading,
                yAxis: 1
        }, {
                type: 'line',
                name: 'Handled requests',
                data: requests,
        }]
        });
    });
};
