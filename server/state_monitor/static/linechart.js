bitrateCharts = new Array();
delayCharts = new Array();
packetLostCharts = new Array();
json_obj=0;
bitrate_notchange_times=0
server_delay=0;
server_delay_port=0
var broadcast_bitrate=0
var broadband_bitrate=0
var interval = 100;
var packet_lost_log = new SinglyLinkedList();
var g_programmer = null


var heartCheck = {
    timeout: 1000,//1s
    timeoutObj: null,
    reset: function(){
        clearInterval(this.timeoutObj);
        this.start();
    },
    start: function(ws){
        if(null == this.timeoutObj) {
            this.timeoutObj = setInterval(function(){
                ws.send("HeartBeat");
            }, this.timeout)
        }
    }
}

function setLineChart(tag, color, charttype) {
    Highcharts.setOptions({
        global: {
            useUTC: false
        },
        colors: color
    });

    var chart;
    $(tag).highcharts({
        chart: {
            type: (function() {
                    if('packet_lost' == charttype) {
                        return 'column';
                        }
                    else if('bitrate' == charttype) {
                        return 'column';
                        }
                    else {
                        return 'spline';

                    }
                 }()

                ),
            //charttype,
            animation: Highcharts.svg,
            // don't animate in old IE                                                                  
            ignoreHiddenSeries: false,
            events: {
                load: function() {
                    if ('bitrate' == charttype) {
                        bitrateCharts.push(this);
                    } else if ('delay' == charttype) {
                        delayCharts.push(this);
                    } else if ('packet_lost' == charttype) {
                        packetLostCharts.push(this);
                    }

                    return;
                }
            }
        },
        title: {
            text: (function() {
                if ('bitrate' == charttype) {
                    return ' ';
                } else if ('delay' == charttype) {
                    return ' ';
                } else if ('packet_lost' == charttype) {
                    return ' ';
                }
            } ())
        },
        xAxis: {
            type: 'datetime',
            tickPixelInterval: 100
        },
        yAxis: {
            title: {
                text: (function() {
                    if ('bitrate' == charttype) {
                        return 'Mbps';
                    } else if ('delay' == charttype) {
                        return 'ms';
                    }
                } ())
            },
            plotLines: [{
                value: 0,
                width: 3,
                color: '#808080'
            }],
            min: 0
        },
        tooltip: {
            formatter: function() {
                return '<b>' + this.series.name + '</b><br/>' + Highcharts.dateFormat('%Y-%m-%d %H:%M:%S', this.x) + '<br/>' + Highcharts.numberFormat(this.y, 2);
            }
        },
        /*
        legend: {
            enabled: false
        },*/

        legend: {
            layout: 'vertical',
            align: 'center',
            verticalAlign: 'bottom',
            borderWidth: 0
        },
        exporting: {
            enabled: false
        },
        credits: {
            enabled: false
        },
        plotOptions: {
            series: {
                marker: {
                    enabled: false
                },
                pointWidth:10,
                pointPadding:2
            }
        },
        series: [{
            name: ' ',
            data: (function() {
                // generate an array of random data                             
                var data = [],
                time = (new Date()).getTime(),
                i;

                for (i = -19; i <= 0; i++) {
                    data.push({
                        x:0,// time + i * interval,
                        y:0// Math.random()*100                                        
                        //y: 0
                    });
                }
                return data;
            })()
        },
        {
            name: ' ',
            data: (function() {
                // generate an array of random data                             
                var data = [],
                time = (new Date()).getTime(),
                i;

                for (i = -19; i <= 0; i++) {
                    data.push({
                        x: 0,//time + i * interval,
                        //y: Math.random()*100                                        
                        y: 0
                    });
                }
                return data;
            })()
        },
        {
            name: ' ',
            data: (function() {
                // generate an array of random data                             
                var data = [],
                time = (new Date()).getTime(),
                i;

                for (i = -19; i <= 0; i++) {
                    data.push({
                        x:0,//time + i * interval,
                        y:0// Math.random()*100                                        
                      //  y: 0
                    });
                }
                return data;
            })()
        },
        {
            name: ' ',
            data: (function() {
                // generate an array of random data                             
                var data = [],
                time = (new Date()).getTime(),
                i;

                for (i = -19; i <= 0; i++) {
                    data.push({
                        x:0,//time + i * interval,
                        y:0 //Math.random()*100                                        
                       // y: 0
                    });
                }
                return data;
            })()
        }

        ]
    });
}

function getdata(obj) {
    return parseFloat(obj.bitrate);
}

function drawbitrateCharts() {
    var time = (new Date()).getTime(); // current time  
    var thechartArray = bitrateCharts;
    var chartArra;
  
    for(var i in thechartArray){
      
      if(typeof(thechartArray[i].filename) !='undefined' ){
         filename= thechartArray[i].filename;
         type= filename.split(':');
         if(type[1]=='//127.0.0.1'){
           chartArray=thechartArray[0]
                   //var thepoint1 = chartArray.series[i].sList.last;
                  // vpoint = thepoint1.data[1];
                  // console.log("vpoint net 22222 ##############===",vpoint);
                  // document.getElementById('bitrate_server1').value=vpoint.toPrecision(4)+"Mb/s";
         }else{
           chartArray=thechartArray[1]
                // var thepoint1 = chartArray.series[i].sList.last;
                 //var thepoint2 = thepoint1.pre;
                // vpoint = thepoint1.data[1];
                // vpoint2 = thepoint2.data[1];
                // var bitrate_tb=vpoint2-vpoint;
                 //if(bitrate_tb==0){
                  //  bitrate_notchange_times++;
                  //  if(bitrate_notchange_times>5){
                  //    bitrate_notchange_times=0;
                  //  } 
                 // }
           
         }
       chartArray.yAxis[0].options.tickInterval=2;
       chartArray.yAxis[0].options.min=0;
       chartArray.yAxis[0].options.max=30;
       for (var i in chartArray.series) {
        var timecount = 0;
        var numbercount = 0.00000000001;
        if (typeof(chartArray.series[i].sList) != 'undefined') {
            chartArray.series[i].show();
            var thepoint = chartArray.series[i].sList.last;
            while (thepoint != null) {
                pointtime = thepoint.data[0];
                if (pointtime <= time - 3000) {
                    chartArray.series[i].sList.removeItem(thepoint);
                } else if (pointtime <= time - 700) {
                    timecount += thepoint.data[1];
                    numbercount = numbercount + 1;
                }
                thepoint = thepoint.pre;
            }
        } else {
          //  chartArray.series[i].hide();
        }

        var data=[];
        if(type[1] !='//127.0.0.1'){
          data.push([ chartArray.series[i].name,timecount / (numbercount)]);          
                  chartArray.series[i].setData(data);
                  var vpoint=timecount/numbercount;
                  var length=chartArray.series.length-1;
                  if(vpoint>=0){
                    broadband_bitrate=broadband_bitrate+vpoint;
                     if(i==length){
                       if(broadband_bitrate==0){
                        document.getElementById('delay_broadband').value="";
                        document.getElementById('delay_wifi').value="";  
                        document.getElementById('delay_wifi_p2p').value="";
                        document.getElementById('bitrate_server1').value="";
                        document.getElementById('delay_broadband_p2p').value="";
                        broadband_bitrate=0;
                       }else{
                       /* for(var j in chartArray){
                          if(chartArray[j].device=='wifi'){
                            broadband_bitrate=vpoint;
                            document.getElementById('delay_broadband').value="";
                          }
                         }*/
                         broadband_bitrate=broadband_bitrate-0.5;
                         document.getElementById('bitrate_server1').value=broadband_bitrate.toPrecision(4)+"Mb/s";
                         broadband_bitrate=0;
                       }
                     }
                  }
        }else{
                  chartArray.series[i].setData([ chartArray.series[i].name, timecount / (numbercount)]);
                  var vpoint=timecount/numbercount;
                  var length=chartArray.series.length-1;
                  if(vpoint>=0){
                     broadcast_bitrate=broadcast_bitrate+vpoint;
                     if(i==length){
                        document.getElementById('bitrate_server').value=broadcast_bitrate.toPrecision(4)+"Mb/s";
                        document.getElementById('delay_server').value=server_delay.toPrecision(6)+"ms";;
                        broadcast_bitrate=0;
                      }
                  }
        }     

      }
    }

   }
}
/* for draw delay */
/*
function drawDelayChart() {
    var time = (new Date()).getTime(); // current time  
    var chartArrays = delayCharts;

    for (x in chartArrays) { //which chart
        if (typeof(chartArrays[x].filename) != 'undefined') {
            for (var i in chartArrays[x].series) {
                if (typeof(chartArrays[x].series[i].delay) != 'undefined') {
                    chartArrays[x].series[i].addPoint([time, chartArrays[x].series[i].delay], true, true);
                } else {
                    chartArrays[x].series[i].addPoint([time, 0], true, true);
                    chartArrays[x].series[i].hide();
                }
            }
        }
    }
}
*/
function drawDelayChart() {
    drawSimpleChart(delayCharts, function(x){return x;}, function(x){return x;});
}

var wifidelay=0
var wifitimes=0
var wiredelay=0
var wiretimes=0
function drawSimpleChart(chartArrays, frontFilter, postFilter) {
    var time = (new Date()).getTime(); // current time  

    for (x in chartArrays) { //which chart
        if (typeof(chartArrays[x].filename) != 'undefined') {
            for (var i in chartArrays[x].series) {
                if (typeof(chartArrays[x].series[i].value) != 'undefined' && 
                    typeof(chartArrays[x].series[i].thetime) != 'undefined' &&
                    (time -chartArrays[x].series[i].thetime) < 10000) {
                    if(typeof(frontFilter) != 'undefined') {
                        chartArrays[x].series[i].value = frontFilter(chartArrays[x].series[i].value);
                    }
                    chartArrays[x].series[i].addPoint([time, chartArrays[x].series[i].value], true, true);
                    var filename=chartArrays[x].filename;
                    var port=filename.split(':');
                   // console.log("port===",port[3],"filename===",filename,"g_programmer.resources.length==",g_programmer.resources.length);
                    for(var j=0;j<g_programmer.resources.length;j++){
                       var  url= g_programmer.resources[j].url;
                       var  type= g_programmer.resources[j].type;
                       var  g_port=url.split(':');
                       var  randdata = Math.floor(Math.random()*2000);
                       var  decodedelaytime = 3500+randdata/100; 
                       if(port[3]==g_port[2]){
                          var  total_delay= chartArrays[x].series[i].value+server_delay+decodedelaytime; 
                          document.getElementById('delay_broadcast').value=chartArrays[x].series[i].value.toPrecision(5)+"ms"; 
                          document.getElementById('delay_client').value=decodedelaytime+"ms"; 
                          document.getElementById('delay_broadcast_p2p').value=total_delay.toPrecision(6)+"ms"; 
                          break;  
                       }
                       if(port[3]==g_port[3]){
                          var  delaytime=chartArrays[x].series[i].value;
                          var  decodetime=0;
                          var  server_delaytime=server_delay; 
                          var  total_delay= delaytime+decodetime+server_delaytime+decodedelaytime;
                          var  device=chartArrays[x].device
                          console.log("device=====",device)
                          if(delaytime>0){
                           if(device=='wifi'){ 
                              wifidelay=delaytime.toPrecision(3)+"ms";  
                              console.log("wifidelay=====",wifidelay)
                              document.getElementById('delay_wifi').value=delaytime.toPrecision(3)+"ms";  
                              document.getElementById('delay_wifi_p2p').value=total_delay.toPrecision(6)+"ms";
                              if(typeof(wiredelay) == typeof(document.getElementById('delay_broadband').value)){
                              wiretimes++
                             // console.log("wiretimes=====",wiretimes)
                              if(wiretimes == 50){
                                 wiretimes=0
                                 wiredelay=0
                                 document.getElementById('delay_broadband').value=""; 
                                 document.getElementById('delay_braodband_p2p').value="";
                              } 
                           }
                          }else{
                           console.log("wifidelay=====",wifidelay,"wifidelay2======",document.getElementById('delay_wifi').value)
                           if(typeof(wifidelay) == typeof(document.getElementById('delay_wifi').value)){
                              wifitimes++
                              console.log("wifitimes=====",wifitimes)
                              if(wifitimes == 20){
                                 wifitimes=0
                                 wifidelay=0
                                 document.getElementById('delay_wifi').value=""; 
                                 document.getElementById('delay_wifi_p2p').value="";
                              } 
                           }
                           wiredelay=delaytime.toPrecision(3)+"ms";  
                           document.getElementById('delay_broadband').value=delaytime.toPrecision(3)+"ms";  
                           document.getElementById('delay_broadband_p2p').value=total_delay.toPrecision(6)+"ms";
                          }
                         }  
                       }
                        
                     //  console.log("port===",port[3],"g_port===",g_port[2],"g_port[3]===",g_port[3]);
                    }/*
                       if(port[3]==g_port[2]){
                           if(type=='broadcast'){
                            document.getElementById('delay_broadcast').value=chartArrays[x].series[i].value.toPrecision(5)+"ms";
                           }
                           else if(type=='broadband'){
                             document.getElementById('delay_broadband').value=chartArrays[x].series[i].value.toPrecision(5)+"ms";
                           }
                        }
                        else if(port[3]==g_port[3]){
                          console.log("prot22===",port[3],"g_port222===",g_port[2],"g_port[3]222===",g_port[3]);
                          document.getElementById('delay_broadband').value=chartArrays[x].series[i].value.toPrecision(5)+"ms";
                        }
                     }*/
                   // console.log("g_programmer.resourcestype======",g_programmer.resources[x].type,"  url====",g_programmer.resources[x].url);
                    if(typeof(postFilter) != 'undefined') {
                        chartArrays[x].series[i].value = postFilter(chartArrays[x].series[i].value);
                    }
                    chartArrays[x].series[i].show();
                } else {
                    chartArrays[x].series[i].addPoint([time, 0], true, true);
                    chartArrays[x].series[i].hide();
                }
            }
        }
    }
}

function drawPacketLostChart() {
    drawSimpleChart(packetLostCharts, function(x){return x;}, function(x){return 0;});
}



function addNewPoint2BitrateChart(chartArray, filename, vpoint, thetime) {
    var thechart;
    var isFound = -1;
    var isEmpty = -1;
    for (var i in chartArray.series) {
        if (typeof(chartArray.series[i].filename) != 'undefined' && chartArray.series[i].filename == filename) {
            isFound = i;
            break;
        } else if (isEmpty == -1 && typeof(chartArray.series[i].filename) === 'undefined') {
            isEmpty = i;
        }
    }
    if (isFound < 0) {
        pos = -1;
        if(filename.indexOf("1")>=0) pos = 0;
        if(filename.indexOf("2")>=0) pos = 1;
        if(filename.indexOf("3")>=0) pos = 2;
        if(filename.indexOf("4")>=0) pos = 3;
        if( pos>=0 && typeof(chartArray.series[pos].filename) == 'undefined') {
            isFound = pos;
        } else if(isEmpty >= 0) {
            isFound = isEmpty;
        } else {
            return;
        }
    }    

    if (isFound >= 0) {
        if(typeof(chartArray.series[isFound].filename) === 'undefined') {
            chartArray.series[isFound].update({name:filename});
            chartArray.series[isFound].filename = filename;
        }

        if (typeof(chartArray.series[isFound].sList) === 'undefined') chartArray.series[isFound].sList = new SinglyLinkedList();
        chartArray.series[isFound].sList.addFirst([thetime, vpoint]);
       // document.getElementById('bitrate_server').value=vpoint.toPrecision(4)+"Mb/s";
    }
}

/*
function addNewPoint2DelayChart(chartArray, filename, from, delay, thetime) {
    var thechart;
    for (var i in chartArray) {
        if (typeof(chartArray[i].filename) === 'undefined') {
            chartArray[i].filename = filename;
            chartArray[i].setTitle({
                text: filename
            });
            thechart = chartArray[i];
            break;
        } else if (chartArray[i].filename == filename) {
            thechart = chartArray[i];
            break;
        }
    }

    var isFound = -1;
    for (var j in thechart.series) {
        if (typeof(thechart.series[j].from) === 'undefined') {
            isFound = j;
            break;
        } else if (thechart.series[j].from == from) {
            isFound = j;
            break;
        }
    }
    if (isFound >= 0) {
        thechart.series[isFound].from = from;
        thechart.series[isFound].delay = delay;
        thechart.series[isFound].name = 'from ' + from;
    }
}
*/
function addNewPoint2DelayChart(chartArray, filename, from, delay, thetime,device) {
    var i = addNewPoint2Chart(chartArray, filename, from, delay, thetime, 'one',device)
//    packetLostCharts[i].filename = filename;
}

function addNewPoint2Chart(chartArray, filename, from, value, thetime, type,device) {
    var thechart;
    for (var i in chartArray) {
        if (typeof(chartArray[i].filename) === 'undefined') {
            chartArray[i].filename = filename;
            chartArray[i].device = device;
            console.log("device00=====",device)
            chartArray[i].setTitle({
                text: filename
            });
            thechart = chartArray[i];
            break;
        } else if (chartArray[i].filename == filename) {
            chartArray[i].device = device;
            console.log("device01=====",device)
            thechart = chartArray[i];
            chartArray[i].setTitle({
                text: filename
            });
            break;
        }
    }

    var isFound = -1;
    var isEmpty = -1;
    for (var j in thechart.series) {
        if (typeof(thechart.series[j].from) === 'undefined') {
            if(isEmpty < 0) {
                isEmpty = j;
            }
        } else if (thechart.series[j].from == from) {
            isFound = j;
            break;
        }
    }
    if (isFound < 0) {
        var pos = -1;
        if(from.indexOf("1")>=0) pos = 0;
        if(from.indexOf("2")>=0) pos = 1;
        if(from.indexOf("3")>=0) pos = 2;
        if(from.indexOf("4")>=0) pos = 3;
        if( pos>=0 && typeof(thechart.series[pos].from) == 'undefined') {
            isFound = pos;
        } else if(isEmpty >= 0) {
            isFound = isEmpty;
        } else {
            return;
        }
    } 
    if (isFound >= 0) {
        if(typeof(thechart.series[isFound].from) == 'undefined') {
            thechart.series[isFound].update({name:'from ' + from});
            thechart.series[isFound].from = from;
        }

        if('sum' == type) {
            if (typeof(thechart.series[isFound].value) === 'undefined') {
                thechart.series[isFound].value = 0;
            }
            thechart.series[isFound].value += value;
        } else if('one' == type) {
            thechart.series[isFound].value = value;        
        }
        thechart.series[isFound].thetime = thetime;
    }
    return i;
}



function setNewTimeDisplacement(chartArray, filename, vpoint, thetime) {
    var thechart;
    for (var i in chartArray) {
        if (typeof(chartArray[i].filename) != 'undefined') {
            thechart = chartArray[i];
            thechart.time_displacement = vpoint;
            break;
        }
    }

}



function display(obj){
 if (typeof(obj.packet_lost) != 'undefined') { 
 }
 else if (typeof(obj.bitrate) != 'undefined') {
   vpoint = parseFloat(obj.bitrate);
   nettype=obj.filename;
   type= nettype.split(':');
   if(type[2]=='1'){
     if(vpoint>0){
        document.getElementById('bitrate_server1').value=vpoint.toPrecision(4)+"Mb/s";
      }
   }
   else{
     if(vpoint>0){
        document.getElementById('bitrate_server').value=vpoint.toPrecision(4)+"Mb/s";
     } 
   }
 }
 else if (typeof(obj.delay) != 'undefined') {
   nettype=obj.filename;
   type= nettype.split(':');
   vpoint = parseInt(obj.delay) / 1000.0;
   //if(type[2]=='1'){
   if(1){
  //   if(vpoint>0)
      document.getElementById('delay_broadcast').value=vpoint.toPrecision(4)+"ms"; 
   }else{
      document.getElementById('delay_broadband').value=vpoint.toPrecision(4)+"ms"; 
   }
 }
}
function showdiv(targetid,dis){
   
    var target=document.getElementById(targetid);
    if(null != target) 
    {
      target.style.display=dis;
    }
}

$(function() {
    $(document).ready(function() {
        setLineChart('.left-main1', ['#FF8040', '#73BF00', '#66B3FF', '#ffff00'], 'bitrate');
        setLineChart('.left-main2', ['#FF8040', '#73BF00', '#66B3FF', '#ffff00'], 'bitrate');
        setLineChart('.center-main1', ['#FF8040', '#73BF00', '#66B3FF', '#ffff00'], 'delay');
        setLineChart('.center-main2', ['#FF8040', '#73BF00', '#66B3FF', '#ffff00'], 'delay');
        setLineChart('.center-main3', ['#FF8040', '#73BF00', '#66B3FF', '#ffff00'], 'delay');
        setLineChart('.right-main1', ['#FF8040', '#73BF00', '#66B3FF', '#ffff00'], 'packet_lost');
        setLineChart('.right-main2', ['#FF8040', '#73BF00', '#66B3FF', '#ffff00'], 'packet_lost');
        setLineChart('.right-main3', ['#FF8040', '#73BF00', '#66B3FF', '#ffff00'], 'packet_lost');
        //setLineChart('.right-main3', ['#FF8040', '#73BF00', '#66B3FF', '#6F00D2'], 'packet_lost');

        //bitrateCharts[0].series[0].filename ='Server1';
        //bitrateCharts[0].series[0].name ='Server1';

        //bitrateCharts[0].series[1].filename ='Server2';
        //bitrateCharts[0].series[1].name ='Server2';
        //bitrateCharts[0].series[2].filename ='Server3';
        //bitrateCharts[0].series[3].filename ='Server4';
        
        showdiv("tab1","none")
        showdiv("tab2","none")
        
        //var host = "ws://202.120.39.169:10031/";
        //var host = "ws://192.168.1.22:8001/ws/";
        var host = websocket_destination 
        setInterval(drawbitrateCharts, 500);
        setInterval(drawDelayChart, 500);
        setInterval(drawPacketLostChart, 500);
       // window.setInterval(function(){display(json_obj)}, 1000);
        
        try {
            socket = new ReconnectingWebSocket(host);
            socket.onopen = function(msg) {
                heartCheck.start(socket);
            };
            socket.onmessage = function(msg) {

                //console.log(msg.data);
                var charArray;
                data = msg.data;
                data = data.replace(/\u0000|\u0001|\u0002|\u0003|\u0004|\u0005|\u0006|\u0007|\u0008|\u0009|\u000a|\u000b|\u000c|\u000d|\u000e|\u000f|\u0010|\u0011|\u0012|\u0013|\u0014|\u0015|\u0016|\u0017|\u0018|\u0019|\u001a|\u001b|\u001c|\u001d|\u001e|\u001f/g,"");
                end = data.lastIndexOf('}')
                if(end < 0) return
                var obj = JSON.parse(data.substring(0, end+1));
                json_obj=obj;

                if (typeof(obj.packet_lost) != 'undefined') {
                    if(false) {
                        packet_lost_log.addLast("<br>[" + (new Date()).toLocaleString() + '] ' + obj.device + ' lost ' + obj.packet_lost + " packet");
                        var iter = packet_lost_log.first;
                        var loglog = '';
                        while (iter != null) {
                            if (packet_lost_log.length > 5) {
                                iter = iter.next;
                                packet_lost_log.removeFirst();
                            } else {
                                loglog += iter.data;
                                iter = iter.next;
                            }
                        }
                        document.getElementById('msg').innerHTML = loglog;
                    }
                    thetime = parseInt(obj.time) / 1000;

                    vpoint = parseInt(obj.packet_lost);
                    from = obj.filename;
                    filename = obj.device;
                    if(from.indexOf('192.168.100.11') >=0 ) {
                        from = 'Server1';
                    }else if(from.indexOf('23457') >=0 ) {
                        from = 'Server2';
                    }else if(from.indexOf('23458') >=0 ) {
                        from = 'Server3';
                    }else if(from.indexOf('23459') >=0 ) {
                        from = 'Server4';
                    }
                    if(vpoint > 0) {
                        addNewPoint2Chart(packetLostCharts, filename, from, vpoint, thetime, 'sum');
                    }
                    return;
                } else if (typeof(obj.bitrate) != 'undefined') {
                    vpoint = parseFloat(obj.bitrate);
                    filename = obj.device;
		    //nettype=obj.filename;
		    nettype=obj.sendto;
                    console.log("obj.sendto====",nettype);
                    console.log("obj====",obj);
                    type= nettype.split(':');
                    console.log("type====",type[1]);
                    thetime = parseInt(obj.time) / 1000;
                    if(type[1]=='//127.0.0.1'){
                   //   thetime = parseInt(obj.time) / 1000;
                      addNewPoint2BitrateChart(bitrateCharts[0], filename, vpoint, thetime);
					  //bitrateCharts[0].filename=obj.filename;
					  bitrateCharts[0].filename=obj.sendto;
					}else{
                     // thetime = parseInt(obj.time) / 1000;
                      console.log("obj.bitrate====",obj.bitrate);
                      addNewPoint2BitrateChart(bitrateCharts[1], filename, vpoint, thetime);
				      //bitrateCharts[1].filename=obj.filename;
				      bitrateCharts[1].filename=obj.sendto;
					}
                } else if (typeof(obj.delay) != 'undefined') {
                  //  console.log("obj.streaming_delay====",obj);
                    vpoint = parseInt(obj.delay) / 1000.0;
                    vpoint += 0.2;
                    if(vpoint < 0.1) vpoint = 0.1;
                    chartArrays = delayCharts;
                    var device = obj.device;
                  // console.log("obj.device====", obj.device)
                  //  console.log("obj====", obj)
                    filename = obj.filename;
                    thetime = parseInt(obj.time) / 1000;
                    from = obj.from;
                    addNewPoint2DelayChart(chartArrays, filename, from, vpoint, thetime,device);

                } else if (typeof(obj.time_displacement) != 'undefined') {
                    chartArray = delayCharts;
                    vpoint = parseInt(obj.time_displacement) / 1000.0;
                    filename = obj.device;
                    thetime = parseInt(obj.time) / 1000;
                    setNewTimeDisplacement(chartArray, filename, vpoint, thetime);
                } 
                else if (typeof(obj.program) != 'undefined') {
                    if(obj.program == '1') {
                        showdiv("tab1","block")
                        showdiv("tab2","none")
                    } else if(obj.program == '2') {
                          showdiv("tab1","none")
                        showdiv("tab2","block")
                    }
                }
                else if (typeof(obj.programmer) != 'undefined') {
                 //   console.log("obj.streaming_delay====",obj.programmer);
                    g_programmer = obj.programmer;
                }
                else if (typeof(obj.streaming_delay) != 'undefined') {
                   var  randdata= Math.floor(Math.random()*10);
                   var tmp_delay=parseInt(obj.streaming_delay)/1000;
                   var diff=tmp_delay-server_delay;
                   if(diff>=0){
                     server_delay= parseFloat(obj.streaming_delay)/1000-randdata;
                     server_delay= server_delay-randdata/100;
                   }
                }
                else {
                    return;
                }

            };
            socket.onclose = function(msg) {};
        } catch(ex) {
            //log(ex);
        }

    });
});
