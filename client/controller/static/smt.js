var program_info_resources = null

function get_resources() {
    return program_info_resources
}
function set_resources(rs) {
    program_info_resources = rs
}


function get_related(){
    $.ajax( {
        type : "GET",
    dataType: "json",
    url : "/show_channels/related_operator/get_related",
    success :displayBt,
    });
}

function set_programme_process_response() {
    $("button.process_resource").click(process_resource_open);
    $("#tv-fullscreen").unbind('click').bind('click',function(){
        console.log("big screen button click")		   
        var	full_id=1
        $.get("/" + $(this).attr('command') +"/"+$(this).attr('channel_id')+"/"+$(this).attr('resource_id')+"/"+full_id+"/",function(ret){

        })
        window.reload_related_operator = true
        $("#device_window").popup("close")
	    if($(this).attr('resource_adurl')!='undefined'){
          window.history.back(-1)
          history.go(1-history.length)
		}
    });
    $("#tv-smallscreen").unbind('click').bind('click',function(){
        console.log("small screen button click")		   
        $.get("/" + $(this).attr('command') +"/"+$(this).attr('channel_id')+"/"+$(this).attr('resource_id')+"/",function(ret){
        })
        window.reload_related_operator = true
        $("#device_window").popup("close")
	    if($(this).attr('resource_adurl')!='undefined'){
          window.history.back(-1)
          history.go(1-history.length)
		}
    })
    $("#pad").unbind('click').bind('click',function(){
        console.log("pad  button click")		   
        $("#device_window").popup("close")
        window.open($(this).attr('resource_url'))			     
    })
   $("button.process_resource_ad").unbind('click').bind('click',function(){
	 window.open( $(this).attr('ad_url'))		
   })
 $("button.process_resource_close").unbind('click').bind('click',function(){
      $.get("/" + $(this).attr('command') +"/"+$(this).attr('channel_id')+"/"+$(this).attr('resource_id')+"/",function(ret){
         }) 		
   })

}


var getFnName = function(callee){
    var _callee = callee.toString().replace(/[\s\?]*/g,""),
        comb = _callee.length >= 50 ? 50 :_callee.length;
    _callee = _callee.substring(0,comb);
    var name = _callee.match(/^function([^\(]+?)\(/);
    if(name && name[1]){
        return name[1];
    }
    var caller = callee.caller,
        _caller = caller.toString().replace(/[\s\?]*/g,"");
    var last = _caller.indexOf(_callee),
        str = _caller.substring(last-30,last);
    name = str.match(/var([^\=]+?)\=/);
    if(name && name[1]){
        return name[1];
    }
    return "anonymous"
}
var last_name=""
var fist_img=0
var arr_url = new Array()
function get_display(url){
    var  len=arr_url.length
    if(len>0){
      for(var i=0;i<len;i++){
         if(arr_url[i] == url){
           return true
         }
      }
    }else{
     return false
    }     
   return false
}
function get_program_list_data() {
    console.log(getFnName(arguments.callee))
    $.get("/currentprogramme/", function(ret){
    //    $("tr.programme_info").remove()
        resources = ret.programmer.resources
        external_resources=ret.programmer.external_resources
        if( typeof(external_resources)=='undefined'){
          $("tr.programme_info").remove()
          arr_url=[]
        }
        set_resources(resources)
      //  console.log(ret.programmer)
        var newtr = ""
        var row=0
        for(var i=0; i< resources.length; i++) {
            newtr = newtr + "<tr class='programme_info'> "
       if(resources[i].info!='embeded_ad'){
		if( typeof(resources[i].added)=='undefined'  ||resources[i].added == 'true'){
        newtr = newtr + "<td > <a href='#'><img src=" + resources[i].poster + " alt=" + resources[i].name +" </td>"
        newtr = newtr + "<td > <button resource_id='" + resources[i].id + "' " 
        + "channel_id='" + ret.channel_id + "' "
        + "resource_url='" + resources[i].url + "' "
		+ "resource_adurl='" + resources[i].adurl +"'"
        + "command='play' " 
        + "class='ui-btn process_resource'>打开</button> </td>"
        newtr = newtr + "<td > <button resource_id='" + resources[i].id + "' " 
        + "channel_id='" + ret.channel_id + "' "
        + "command='stop' " 
        + "class='ui-btn process_resource_close'>关闭</button> </td>"
       /* if(resources[i].adurl!=null&&resources[i].adname!=null){
            newtr = newtr + "<td > <button ad_url='" + resources[i].adurl + "' " 
        + "class='process_resource_ad'>"+resources[i].adname+"</button> </td>"
        }*/
        newtr = newtr + "</tr>"
		}
	   }else{
		 if(i>0){
		 //  console.log("begintime=======",resources[i].display)
		   if(resources[i].display=='1'){
                     var ret=get_display(resources[i].poster)
                     if(ret){
                         continue  
                     }
            newtr = newtr + "<td > <a href='#'><img src=" + resources[i].poster + " alt=" + resources[i].name +" </td>"
            newtr = newtr + "<td > <button ad_url='" + resources[i].adurl + "' " 
                          + "class='process_resource_ad'>购买</button> </td>"
			last_name= resources[i].poster
                        arr_url.push(resources[i].poster)
		   }
           newtr = newtr + "</tr>"
		 }
	   }
     }
    $("#programmeinfo").prepend(newtr);
    $("#programmeinfo").trigger('create');
    set_programme_process_response()

    })
}


function process_resource_open() {
    console.log(getFnName(arguments.callee))
    window.jxj = 2
    resources = get_resources()
    if(null == resources) { return }
    $("button.devicelist").remove()
    newtr = " <li><button  id='tv-fullscreen'"  + "resource_id='" 
        + $(this).attr('resource_id') + "' " 
        + "channel_id='" + $(this).attr('channel_id') + "' "
        + "resource_adurl='" + $(this).attr('resource_adurl') + "' "
        + "class='ui-btn ui-btn-icon-right ui-icon-carat-r devicelist' "
        + "command='play'" +">电视(全屏）</button></li>" 
        + " <li><button  id='tv-smallscreen'"  + "resource_id='" 
        + $(this).attr('resource_id') + "' " 
        + "channel_id='" + $(this).attr('channel_id') + "' "
        + "resource_adurl='" + $(this).attr('resource_adurl') + "' "
        + "class='ui-btn ui-btn-icon-right ui-icon-carat-r devicelist' "
        + "command='play'" +">电视(小屏）</button></li>" 
        + "<li> <button  id='pad'" +"'" + "resource_id='" 
        + $(this).attr('resource_id') + "' " 
        + "channel_id='" + $(this).attr('channel_id') + "' "
        + "resource_url='" + $(this).attr('resource_url') + "' "
        + "class='ui-btn ui-btn-icon-right ui-icon-carat-r devicelist' "
        + "command='play' " +">便携终端</button></li>"
    console.log(newtr)		   
    $("#devicelist").append(newtr)
    $("#device_window").popup("open", { transition:"slideup", positionTo:"window"})
    set_programme_process_response()
}

function set_pause() {
   $.get("/show_channels/command/",{ command:"render"})
}
function set_hide() {
   $.get("/show_channels/command/",{ command:"hide"})
}


