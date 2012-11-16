var incoming_data;
var ideal_tomato = [0.2, 0.2, 1, 0.95, 0.9, 0.75, 0.6, 0.4, 0.2];

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
        if (typeof(incoming_data) == 'undefined') return;

        var data = new google.visualization.DataTable();
        // add columns
        data.addColumn('datetime', 'date');
        data.addColumn('number', 'ideal %moisture');
        data.addColumn('number', 'recorded %moisture');
        // add empty rows
        data.addRows(incoming_data.length)
        // populate the rows
	// go over the incoming data variable
        for (var row = 0; row < incoming_data.length; ++row) {
          for (var date in incoming_data[row]) {
            // multiply by 1000 so that the date is in milliseconds, not seconds
	    data.setCell(row, 0, new Date(parseInt(date) * 1000));
            data.setCell(row, 1, ideal_tomato[row]);
            data.setCell(row, 2, parseFloat(incoming_data[row][date]));
          }
        }

        var formatter = new google.visualization.DateFormat({pattern: "EEE, MMM d, H:m"});
        formatter.format(data,0);

        var options = {
          title: 'Tomatoes',
          hAxis: {
            format: 'EEE, MMM d, H:mm'
          }
        };

        var chart = new google.visualization.LineChart(document.getElementById('tomato_chart_div'));
        chart.draw(data, options);
      }
