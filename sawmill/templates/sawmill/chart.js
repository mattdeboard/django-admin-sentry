<script type="text/javascript">
var activityChart;
$(document).ready(function () {
        chart1 = new Highcharts.Chart({
                chart: {
                    renderTo: 'chart',
                    zoomType: 'x',
                    backgroundColor: '#444',
                    height: 200
                },

                title: {
                    text: 'User Activity'
                },

                xAxis: {
                    type: 'datetime',
                    dateTimeLabelFormats: {
                        second: '%H:%M:%S',
                        minute: '%H:%M',
                        hour: '%d %b %H:%M',
                        day: '%e. %b',
                        week: '%e. %b',
                        month: '%b \'%y',
                        year: '%Y'
                    }
                },

                yAxis: {
                    title: {
                        text: false
                    }
                },

                series: [{
                        name: "Dates",
                        pointStart: new Date() - {{ log_dates.dates|first }} * 360000
                        pointInterval: 3600 * 1000,
                        type: 'area'
            });
    });
        </script>

                
                    