bitrateCharts = new Array();
delayCharts = new Array();
packetLostCharts = new Array();
json_obj=0
var interval = 100;
var packet_lost_log = new SinglyLinkedList();

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
	     if(type[2]=='1'){
	//	   console.log("filename@@@@@@@@@@@@@@@==1")
		   chartArray=thechartArray[1]
	     }else{
		   chartArray=thechartArray[0]
	//	   console.log("filename@@@@@@@@@@@@@@@==0",filename)
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
	    if(type[2]=='1'){
		  data.push([ chartArray.series[i].name,timecount / (numbercount)]);		  
          chartArray.series[i].setData(data);
		}else{
           chartArray.series[i].setData([ chartArray.series[i].name, timecount / (numbercount)]);
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

function drawSimpleChart(chartArrays, frontFilter, postFilter) {
    var time = (new Date()).getTime(); // current time  

    for (x in chartArrays) { //which chart
        if (typeof(chartArrays[x].filename) != 'undefined') {
            for (var i in chartArrays[x].series) {
                if (typeof(chartArrays[x].series[i].value) != 'undefined' && 
                    typeof(chartArrays[x].series[i].thetime) != 'undefined' &&
                    (time -chartArrays[x].series[i].thetime) < 10000) {
                    //console.log("the dtime is",time -(chartArrays[x].series[i].thetime));
                    if(typeof(frontFilter) != 'undefined') {
                        chartArrays[x].series[i].value = frontFilter(chartArrays[x].series[i].value);
                    }
                    chartArrays[x].series[i].addPoint([time, chartArrays[x].series[i].value], true, true);
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
function addNewPoint2DelayChart(chartArray, filename, from, delay, thetime) {
    var i = addNewPoint2Chart(chartArray, filename, from, delay, thetime, 'one')
    packetLostCharts[i].filename = filename;
}

function addNewPoint2Chart(chartArray, filename, from, value, thetime, type) {
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
   console.log("display%%%%%%%%%==",type[2])
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
	 alert("delay&&&&&&&&&&&&&&&&&&&&&&")
     vpoint = parseInt(obj.delay) / 1000.0;
	 console.log("delay##############vpoint",vpoint)
   if(vpoint>0)
     document.getElementById('delay_broadcast').value=vpoint.toPrecision(4)+"s";  
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
        window.setInterval(function(){display(json_obj)}, 1000);
        
        try {
            socket = new ReconnectingWebSocket(host);
            socket.onopen = function(msg) {
                //log('Connected');
            };
            socket.onmessage = function(msg) {

                //console.log(msg.data);
                var charArray;
                data = msg.data;

                
                var obj = JSON.parse(data);
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
					nettype=obj.filename;
                    type= nettype.split(':');
                    console.log("type=",type[2])				
                    thetime = parseInt(obj.time) / 1000;
                    if(type[2]=='1'){
                   //   thetime = parseInt(obj.time) / 1000;
                      console.log("vpoint=",vpoint)				
                      addNewPoint2BitrateChart(bitrateCharts[1], filename, vpoint, thetime);
				      bitrateCharts[1].filename=obj.filename;
					}else{
                     // thetime = parseInt(obj.time) / 1000;
                      addNewPoint2BitrateChart(bitrateCharts[0], filename, vpoint, thetime);
					  bitrateCharts[0].filename=obj.filename;
					}
                } else if (typeof(obj.delay) != 'undefined') {
                    //console.log('data=', data);
                    vpoint = parseInt(obj.delay) / 1000.0;
                    vpoint += 0.2;
                    if(vpoint < 0.1) vpoint = 0.1;
                    chartArrays = delayCharts;
                    filename = obj.device;
                    thetime = parseInt(obj.time) / 1000;
                    from = obj.from;
                    addNewPoint2DelayChart(chartArrays, filename, from, vpoint, thetime);

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
