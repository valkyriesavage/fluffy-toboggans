var NUM_POINTS = 30;

var incoming_data = [];
var display_data = [];
var ideal_tomato = [10, 15, 20, 26, 38, 49, 59, 70, 89, 95, 100, 99, 87, 76, 65, 58, 50, 45, 38, 30, 25, 20, 14, 10, 10, 10, 10, 10, 10, 10];
var water_flag = false;
var ticker = [];

$(document).ready(function() {
  // initialize tickers
  for (var i = 0; i < NUM_POINTS; ++i) {
    ticker.push(0);
  }

  // post the new instructions to the watering system
  $(".waterform").live("submit", function() {
    newInstruction($(this));
    water_flag = true;
    return false;
  });

  // toggle between modes
  $("#toggleform-manual").live("submit", function() {
    document.getElementById('wd-form-manual').style.display='none';
    document.getElementById('wd-form-auto').style.display='block';
    document.getElementById('wd-form-toggle-manual').style.display='none';
    document.getElementById('wd-form-toggle-auto').style.display='block';
    return false;
  });

  $("#toggleform-auto").live("submit", function() {
    document.getElementById('wd-form-auto').style.display='none';
    document.getElementById('wd-form-manual').style.display='block';
    document.getElementById('wd-form-toggle-auto').style.display='none';
    document.getElementById('wd-form-toggle-manual').style.display='block';
    return false;
  });

  // graph the new moisture readings
  updater.start();
});

function newInstruction(form) {
  var instruction = form.formToDict();
  updater.socket.send(JSON.stringify(instruction));
  form.find("input[type=text]").val("").select();
}

jQuery.fn.formToDict = function() {
  var fields = this.serializeArray();
  var json = {}
  for (var i = 0; i < fields.length; i++) {
    json[fields[i].name] = fields[i].value;
  }
  if (json.next) delete json.next;
  return json;
};


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
    // append our data to existing data
    incoming_data.push.apply(incoming_data, incoming);
    display_data = incoming_data.slice(incoming_data.length-NUM_POINTS-1, incoming_data.length);
    if (water_flag == true) {
      ticker[ticker.length - incoming.length] = 1;
      water_flag = false;
    } else {
      // move the ticker position in time with the data
      for (var i = 0; i < incoming.length; ++i) {
        ticker.shift();
        ticker.push(0);
      }
    }
    drawChart();
  }
};

google.load("visualization", "1", {packages:["annotatedtimeline"]});
google.setOnLoadCallback(drawChart);

function drawChart() {
  if (typeof(incoming_data) == 'undefined') return;

  var data = new google.visualization.DataTable();
  // add columns
  data.addColumn('datetime', 'date');
  data.addColumn('number', 'ideal %moisture');
  data.addColumn('number', 'recorded %moisture');
  data.addColumn('string', 'title1');
  // add empty rows
  data.addRows(display_data.length);
  // populate the rows
  // go over the incoming data variable
  for (var row = 0; row < display_data.length; ++row) {
    for (var date in display_data[row]) {
      // multiply by 1000 so that the date is in milliseconds, not seconds
      data.setCell(row, 0, new Date(parseInt(date) * 1000));
      data.setCell(row, 1, ideal_tomato[row]);
      data.setCell(row, 2, parseFloat(display_data[row][date]));
      if (1 == ticker[row]) {
        data.setCell(row, 3, 'watered');
      } else {
        data.setCell(row, 3, undefined);
      }
    }
  }

  var formatter = new google.visualization.DateFormat({pattern: "EEE, MMM d, H:m"});
  formatter.format(data,0);

  var options = {
    title: 'Tomatoes',
    hAxis: {
      format: 'EEE, MMM d, H:mm'
    },
    displayAnnotations: true
  };

  var chart = new google.visualization.AnnotatedTimeLine(document.getElementById('tomato_chart_div'));
  chart.draw(data, options);
}
