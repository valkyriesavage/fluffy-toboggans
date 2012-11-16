var incoming_data;

$(document).ready(function() {
	// post the new instructions to the watering system
	// TODO

	// graph the new moisture readings
	updater.start();
});

var updater = {
	socket: null,

	start: function() {
		var url = "ws://" + location.host + "/plant/plant_1";
		if ("WebSocket" in window) {
			updater.socket = new WebSocket(url);
		} else {
			updater.socket = new MozWebSocket(url);
		}
		updater.socket.onmessage = function(event) {
                        // parse the incoming JSON into a JavaScript array
                        // of Javascript Objects containig property,value pairs
			updater.updateIncoming(JSON.parse(event.data));
		}
	},

	updateIncoming: function(incoming) {
		// TODO what is the format of data coming in?
		// TODO update the incoming data variable
		incoming_data = incoming;
                drawChart();
	}
};

google.load("visualization", "1", {packages:["corechart"]});
      google.setOnLoadCallback(drawChart);
      function drawChart() {
        /*
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
*/
        if (typeof(incoming_data) == "undefined") return;

        var data = new google.visualization.DataTable();
        // add columns
        //data.addColumn('date', 'date'); TODO switch to date and format
        data.addColumn('number', 'date');
        data.addColumn('number', 'ideal %moisture');
        data.addColumn('number', 'recorded %moisture');
        // add empty rows
        data.addRows(incoming_data.length)
        // populate the rows
	// go over the incoming data variable
        for (var row = 0; row < incoming_data.length; ++row) {
          for (var date in incoming_data[row]) {
	    data.setCell(row, 0, parseFloat(date));
            data.setCell(row, 1, 1);
            data.setCell(row, 2, parseFloat(incoming_data[row][date]));
          }
        }

        var options = {
          title: 'Tomatoes'
        };

        var chart = new google.visualization.LineChart(document.getElementById('tomato_chart_div'));
        chart.draw(data, options);
      }
