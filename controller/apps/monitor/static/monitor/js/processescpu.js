function processescpu(url, tag, keys) {
    var seriesOptions = [],
        yAxisOptions = [],
        seriesCounter = 0,
        colors = Highcharts.getOptions().colors;
    
    $.getJSON(url, function(data) {
        var dataLength = data.length;
        var previous = [];
        $.each(keys, function(i, name) {
            var current = [];
            for (j = 0; j < dataLength; j++) {
                previous[j] = previous[j] || 0;
                var actual = previous[j]+data[j][1]['current-'+name];
                current.push([
                    data[j][0],
                    previous[j],
                    actual
                ]);
                previous[j] = actual;
            };
            seriesOptions[i] = {
                name: name,
                data: current
            };
        });
    createChart();
    });
    
    // create the chart when all data is loaded
    function createChart() {
        $('#'+tag).highcharts('StockChart', {
            chart: {
                type: 'arearange'
            },
            rangeSelector: {
                selected: 4
            },
            yAxis: {
            	plotLines: [{
            		value: 0,
            		width: 2,
            		color: 'silver'
            	}]
            },
            
//            plotOptions: {
//            	series: {
//            		compare: 'percent'
//            	}
//            },
//            
//            tooltip: {
//            	pointFormat: '<span style="color:{series.color}">{series.name}</span>: <b>{point.y}</b> ({point.change}%)<br/>',
//            	valueDecimals: 2
//            },
            
            series: seriesOptions
        });
    }
};
