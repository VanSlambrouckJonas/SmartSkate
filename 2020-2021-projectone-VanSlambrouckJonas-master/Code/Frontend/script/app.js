'use strict';

const provider = 'https://{s}.tile.openstreetmap.fr/hot/{z}/{x}/{y}.png';
const copyright = '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors, Tiles style by <a href="https://www.hotosm.org/" target="_blank">Humanitarian OpenStreetMap Team</a> hosted by <a href="https://openstreetmap.fr/" target="_blank">OpenStreetMap France</a>';

let map, layergroup;
let mapmade = 0;
const lanIP = `${window.location.hostname}:5000`;
const socket = io(`http://${lanIP}`);

let htmlmenu, htmlchart, htmlBattery, htmlKm, htmlAmountRides, htmlMaxSpeed, htmlAvgSpeed, htmlsidenav, htmlpower, htmlhoverdiv, htmlspecificmap;
let sidenavOpen = 0;

function drawVoltageChart(labels1, data1, labels2, data2) {
  var options1 = {
    series: [{
    name: 'Battery left in %',
    data: data1
  }],
    chart: {
      height: '90%',
      width: '100%',
      type: 'area'
  },
  dataLabels: {
    enabled: false
  },
  stroke: {
    curve: 'smooth'
  },
  xaxis: {
    type: 'datetime',
    categories: labels1
  },
  tooltip: {
    x: {
      format: 'dd/MM/yy HH:mm'
    },
  },
  };

  var options2 = {
    series: [{
    name: 'Voltage',
    data: data2
  }],
    chart: {
      height: '90%',
      width: '100%',
      type: 'area'
  },
  dataLabels: {
    enabled: false
  },
  stroke: {
    curve: 'smooth'
  },
  xaxis: {
    type: 'datetime',
    categories: labels2
  },
  tooltip: {
    x: {
      format: 'dd/MM/yy HH:mm'
    },
  },
  };

  var chart1 = new ApexCharts(document.querySelector(".js-chart1"), options1);
  var chart2 = new ApexCharts(document.querySelector(".js-chart2"), options2);
  document.querySelector('.js-chart1').innerHTML = ``
  document.querySelector('.js-chart2').innerHTML = ``
  chart1.render();
  chart2.render();
}

function drawkmChart() {
  var options = {
    series: [10],
    chart: {
    height: '64px',
    width: '64px',
    type: 'radialBar',
  },
  plotOptions: {
    radialBar: {
      hollow: {
        size: '20%',
      }
    },
  },
  labels: ['8km'],
  };

  var chart = new ApexCharts(document.querySelector(".js-circlechart"), options);
  chart.render();
}

function drawCircleChart(value1, value2) {
  console.log(value1, "     ", value2)
  let htmlcircle = document.querySelector(".js-chart3")
  if(value1 == 0 & value2 == 0){
    htmlcircle.innerHTML = `<p style='top-margin: 24px'>No data given</p>`
  }
  else {
    var options = {
      series: [value1 * 2.5, value2 * 2.5],
      colors: ["#6AC9C6", "#EF7676"],
      chart: {
      height: 224,
      type: 'radialBar',
    },
    plotOptions: {
      radialBar: {
        dataLabels: {
          name: {
            fontSize: '28px',
          },
          value: {
            fontSize: '18px',
          },
          total: {
            show: true,
            label: 'stats',
            formatter: function (w) {
              // By default this function returns the average of all series. The below is just an example to show the use of custom formatter function
              return "click me"
            }
          }
        }
      }
    },
    labels: ['Max Speed', 'Avg Speed'],
    };
  
    var chart = new ApexCharts(document.querySelector(".js-chart3"), options);
    htmlcircle.innerHTML = ``
    chart.render();
  }
}

const showData = function(data){
  console.log(data);

  let converted_labels1 = [];
  let converted_data1 = [];
  let converted_labels2 = [];
  let converted_data2 = []; 
  var arr_coords1 = [];
  var arr_coords2 = [];
  let lat = [];
  let long = [];
  let avgspeed;
  let maxspeed;
  let title;
  let description;
  let date
  for (const voltage of data){
    if(voltage.deviceID == 4){
      converted_labels1.push(voltage.date);
      converted_data1.push(voltage.value);
    }
    else if(voltage.deviceID == 3){
      converted_labels2.push(voltage.date);
      converted_data2.push(voltage.value);
    }
    else if(voltage.deviceID == 1){
      lat.push(voltage.value);
    }
    else if(voltage.deviceID == 2){
      long.push(voltage.value);
    }
    avgspeed = voltage.avgSpeed;
    maxspeed = voltage.maxSpeed;
    if(title == null){
      title = voltage.sessionID;
      description = voltage.description;
    }
    if(date == null){
      date = voltage.startDate;
      console.log(date);
    }
  }

  document.querySelector('.js-title').innerHTML = `Ride ${title}`;
  if(description != null){
    document.querySelector('.js-description').innerHTML = `${description}`;
  }
  else{
    document.querySelector('.js-description').innerHTML = `no description`;
  }

  document.querySelector('.js-rideDate').innerHTML = `${date}`

  console.log("length arr: ", lat.length, "   ", long.length);
  if(htmlspecificmap){
    if(lat.length > 1 & long.length > 1){
      arr_coords1.push(lat[0]);
      arr_coords1.push(long[0]);
      arr_coords2.push(lat[lat.length - 1]);
      arr_coords2.push(long[long.length - 1]);
      console.log(lat[lat.length -1])
      console.log("latitude: " + arr_coords1[0] + "    longitude: " + arr_coords1[1])
      if(mapmade == 0){
        console.log("make container");
        map = L.map("mapid").setView([arr_coords1[0], arr_coords1[1]], 14);
        L.tileLayer(provider, { attribution: copyright }).addTo(map)
        layergroup = L.layerGroup().addTo(map);
        mapmade = 1;
      }
      else{
        layergroup.clearLayers();
      }
      

      let marker1 = L.marker(arr_coords1).addTo(layergroup);
      marker1.bindPopup(`<h3>Start Location</h3><em>${arr_coords1}</em>`);

      let marker2 = L.marker(arr_coords2).addTo(layergroup);
      marker2.bindPopup(`<h3>End Location</h3><em>${arr_coords2}</em>`);
    }
    else{
      layergroup.clearLayers();
    }
  }

  drawVoltageChart(converted_labels1, converted_data1, converted_labels2, converted_data2);
  if(htmlchart){
    if(maxspeed != null & avgspeed != null){
      drawCircleChart(maxspeed, avgspeed);
    }
    else{
      drawCircleChart(25, 16);
    }
    
  }
}

const showAllRides = function(data){
  console.log(data);

  let htmlAllRides = document.querySelector('.js-allRides');
  let html = `<h1>All Rides</h1>`
  for(const stat of data){
    html += `<div style="width: 224px; height: 128px; margin-top: 16px;" data-ride-id="${stat.sessionID}"  class="o-layout__item__contentAllRides o-white-back js-allrides">
              <div style="display: inline-flex;">
                <div class="o-layout__centering">
                  <h2>
                    Ride ${stat.sessionID}
                  </h2> 
                </div>
              </div>
              <div>
                <p>${stat.startDate}</p> 
              </div>
            </div>`
  }

  htmlAllRides.innerHTML = html;
  listenToUI();
}

const showStats = function (jsonObject) {
  console.log(jsonObject);
  htmlKm.innerHTML = `${Math.round(jsonObject[0].distance * 1000) / 1000}km in total`
  htmlAmountRides.innerHTML = `${jsonObject[0].amount} rides in total`
  htmlMaxSpeed.innerHTML = `${Math.round(jsonObject[0].maxSpeed)} km/h max`
  htmlAvgSpeed.innerHTML = `${Math.round(jsonObject[0].avgSpeed)} km/h avg`
}

const maakMaker = function(jsonObject){
  console.log('in maakMaker')
  var arr_coords = [];
  let lat
  let long
  for(const values of jsonObject.data){
    console.log(values);
    if(values.deviceID == 1){
      lat = values.value;
    }
    else if(values.deviceID == 2){
      long = values.value;
    }
  }

  arr_coords.push(lat);
  arr_coords.push(long);
  
  map = L.map("mapid").setView([lat, long], 14);
  L.tileLayer(provider, { attribution: copyright }).addTo(map)
  layergroup = L.layerGroup().addTo(map);

  let marker = L.marker(arr_coords).addTo(layergroup);
  marker.bindPopup(`<h3>Last known location</h3><em>${arr_coords}</em>`);
}

function listenToUI() {
  console.log("in listentoUI")
  htmlmenu.addEventListener("click", () => {
    console.log("menu has been klicked");
    htmlsidenav.classList.add("displaynone");
    sidenavOpen = 1
  });

  htmlhoverdiv.addEventListener("click", () => {
    console.log("div has been klicked");
    htmlsidenav.classList.remove("displaynone");
    sidenavOpen = 0;      
  });

  htmlpower.addEventListener("click", () => {
    console.log("power has been klicked");
    socket.emit("F2B_power_off");
  });
  const rides = document.querySelectorAll('.js-allrides');
  for (const ride of rides) {
    ride.addEventListener('click', function () {
      window.scrollTo(0,0);
      const id = ride.getAttribute('data-ride-id');
      console.log("rideID: ", id)
      console.log("ride has been clicked");
      socket.emit("F2B_get_ridedata", id);
    });
  }
};

const listenToSocket = function () {
  socket.on("connected", function (jsonObject) {
    console.log("init connection")
    console.log("verbonden met socket webserver");
    console.log(jsonObject);
  });

  if(htmlBattery){
    socket.on("B2F_currentVoltage", function (jsonObject) {
      console.log(jsonObject);
      let val = 0
      for(const value of jsonObject.data){
        val = value.value
      }
      console.log(val)
      val = Math.round(val)
      if(val >= 0){
        htmlBattery.innerHTML = `${val}% battery left`
      }
      else{
        htmlBattery.innerHTML = `disconnected`
      }
    });

    socket.on("B2F_basicStats", function (jsonObject) {
      console.log(jsonObject);
      showStats(jsonObject.data)
    });

    socket.on("B2F_currentgps", function (jsonObject) {
      console.log(jsonObject);
      maakMaker(jsonObject);
    });
  }
  else{
    socket.on("B2F_AllRides", function (jsonObject) {
      console.log("all ridedata: ")
      showAllRides(jsonObject.data);
    });
    socket.on("B2F_ride", function (jsonObject) {
      console.log("ridedata: ")
      console.log(jsonObject.data);
      showData(jsonObject.data);
    });
  }
};

document.addEventListener("DOMContentLoaded", function () {
  console.info("DOM geladen");

  htmlchart = document.querySelector('.js-chart1');
  htmlmenu = document.querySelector('.js-menu');
  htmlsidenav = document.querySelector('.js-sidenav');
  htmlBattery = document.querySelector('.js-batteryPercentage');
  htmlKm = document.querySelector('.js-totalKm');
  htmlAmountRides = document.querySelector('.js-amountOfRides');
  htmlMaxSpeed = document.querySelector('.js-maxSpeed');
  htmlAvgSpeed = document.querySelector('.js-avgSpeed');
  htmlpower = document.querySelector('.js-power');
  htmlhoverdiv = document.querySelector('.js-divhover');
  htmlspecificmap = document.querySelector('.js-specific-map');

  if(htmlBattery){
    
  }
  else{
    drawkmChart();
  }

  listenToSocket();
  listenToUI();
});
