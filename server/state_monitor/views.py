# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.shortcuts import render
import websocketserver
from django.http import HttpResponse
from websocketserver import WebSocket
from state_monitor.models import get_monitor_settings
from potal.models import get_userinfo_settings 
from potal.models import UserInfo
import json
def check_username(username):
   userinfo=get_userinfo_settings() 
   for userlist in userinfo:
      if username==userlist.user:
         return 1 
   return 0
def show_status(request):
  name=request.COOKIES.get('username','1')
  ret=check_username(name)
  if (ret):
    monitor_settings = get_monitor_settings()   
    if request.GET.has_key('version') and request.GET['version'] == 'fe85884':
        return render(request, 'index-fe85884.html', {'monitor_settings':monitor_settings}) 
    else:
        return render(request, 'index.html', {'monitor_settings':monitor_settings})
  else:
    url=request.get_full_path()
    return render(request,'login.html',{'url':url})
def start_state_monitor(request):
    print 'start info server'
    monitor_settings = get_monitor_settings()   
    websocketserver.start_info_server(monitor_settings.info_collector_ip,  
                                      monitor_settings.info_collector_port,
                                      monitor_settings.info_websocket_ip,
                                      monitor_settings.info_websocket_port)

    return HttpResponse(u'OK', content_type='applicatoin/json')

def connect_websocket(request):
    print "websocket"
    return HttpResponse('OK', content_type='applicatoin/json')

def websocket_connection_num(request):
    num =  websocketserver.get_connectonlist_length()
    ret={}
    ret["websocket_connection_num"]=num
    return HttpResponse(json.dumps(ret), content_type='applicatoin/json')


