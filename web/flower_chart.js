google.load("visualization", "1", {packages:["corechart"]});
      google.setOnLoadCallback(drawChart);
      function drawChart() {
        var data = google.visualization.arrayToDataTable([
          ['time', 'ideal %moisture', 'recorded %moisture'],
          ['Sun',  10,       10],
          ['Mon',  100,      90],
          ['Tue',  80,      90],
          ['Wed',60,      70],
          ['Thu',  20,     60],
          ['Fri',  10,       50],
          ['Sat', 10,      40]
        ]);

        var options = {
          title: 'Tomatoes'
        };

        var chart = new google.visualization.LineChart(document.getElementById('tomato_chart_div'));
        chart.draw(data, options);
      }