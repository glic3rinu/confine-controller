function stategraph(url) {
    $.getJSON(url, function(data) {
        var start = + new Date();
        $('#statechart').highcharts({
        chart: {
            type: 'column'
        },
        credits: {
            enabled: false
        },
        title: {
            text: false
        },
        subtitle: {
            text: false
        },
        xAxis: {
            categories: data['categories'],
            tickmarkPlacement: 'on',
            title: {
                enabled: false
            }
        },
        yAxis: {
            title: {
                text: 'Percent'
            }
        },
        tooltip: {
            pointFormat: '<span style="color:{series.color}">{series.name}</span>: <b>{point.percentage:.1f}%</b> ({point.y:,.0f} seconds)<br/>',
            shared: true
        },
        plotOptions: {
            column: {
                stacking: 'percent',
                lineColor: '#ffffff',
                lineWidth: 1,
                marker: {
                    lineWidth: 1,
                    lineColor: '#ffffff'
                }
            }
        },
        series: data['series']
        });
    });
};
