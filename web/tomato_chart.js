var incoming_data;

$(document).ready(function() {
	// post the new instructions to the watering system
	// TODO

	// graph the new moisture readings
	document.getElementById('tomato_chart_div').select();
	updater.start();
});

var updater = {
	socket: null,

	start: function() {
		var url = "ws://" + location.host + "/plant/"; //TODO
		if ("WebSocket" in window) {
			updater.socket = new WebSocket(url);
		} else {
			updater.socket = new MozWebSocket(url);
		}
		updater.socket.onmessage = function(event) {
			updater.updateIncoming(JASON.parse(event.data));
		}
	},

	updateIncoming: function(incoming) {
		// TODO what is the format of data coming in?
		// TODO update the incoming data variable
	}
};

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

		// TODO go over the incoming data variable
		// data.setCell(fill me in);

        var options = {
          title: 'Tomatoes'
        };

        var chart = new google.visualization.LineChart(document.getElementById('tomato_chart_div'));
        chart.draw(data, options);
      }
