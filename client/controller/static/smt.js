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
    $("#tv-fullscreen").click(function(){
        console.log("big screen button click")		   
        var	full_id=1
        $.get("/" + $(this).attr('command') +"/"+$(this).attr('channel_id')+"/"+$(this).attr('resource_id')+"/"+full_id+"/",function(ret){

        })
        $("#device_window").popup("close")
        window.history.back(-1)
    });
    $("#tv-smallscreen").click(function(){
        console.log("small screen button click")		   
        $.get("/" + $(this).attr('command') +"/"+$(this).attr('channel_id')+"/"+$(this).attr('resource_id')+"/",function(ret){
        })
        $("#device_window").popup("close")
    })
    $("#pad").click(function(){
        console.log("pad  button click")		   
        $("#device_window").popup("close")
        gotoActivity('videoactivity')			     
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
function get_program_list_data() {
    console.log(getFnName(arguments.callee))
    $.get("/currentprogramme/", function(ret){
        $("tr.programme_info").remove()
        resources = ret.programmer.resources
        set_resources(resources)
        console.log(resources)
        var newtr = ""
        for(var i=0; i< resources.length; i++) {
            newtr = newtr + "<tr class='programme_info'> "
        console.log(resources[i].poster)
        newtr = newtr + "<td > <a href='#'><img src=" + resources[i].poster + " alt=" + resources[i].name +" </td>"
        newtr = newtr + "<td > <button resource_id='" + resources[i].id + "' " 
        + "channel_id='" + ret.channel_id + "' "
        + "resource_url='" + resources[i].url + "' "
        + "command='play' " 
        + "class='ui-btn process_resource'>打开</button> </td>"
        newtr = newtr + "<td > <button resource_id='" + resources[i].id + "' " 
        + "channel_id='" + ret.channel_id + "' "
        + "command='stop' " 
        + "class='ui-btn process_resource_close'>关闭</button> </td>"
        if(resources[i].adurl!=null&&resources[i].adname!=null){
            newtr = newtr + "<td > <button ad_url='" + resources[i].adurl + "' " 
        + "class='process_resource_ad'>"+resources[i].adname+"</button> </td>"
        }
    newtr = newtr + "</tr>"
        }
    $("#programmeinfo").append(newtr)
        set_programme_process_response()

    })
}


function process_resource_open() {
    console.log(getFnName(arguments.callee))
    resources = get_resources()
    if(null == resources) { return }
    $("button.devicelist").remove()
    newtr = " <li><button  id='tv-fullscreen'"  + "resource_id='" 
        + $(this).attr('resource_id') + "' " 
        + "channel_id='" + $(this).attr('channel_id') + "' "
        + "class='ui-btn ui-btn-icon-right ui-icon-carat-r devicelist' "
        + "command='play'" +">电视(全屏）</button></li>" 
        + " <li><button  id='tv-smallscreen'"  + "resource_id='" 
        + $(this).attr('resource_id') + "' " 
        + "channel_id='" + $(this).attr('channel_id') + "' "
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




