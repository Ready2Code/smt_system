# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.shortcuts import render
from django.http import HttpResponse

from signal_server import start_smt_system
from signal_server import stop_all
import threading
from service_manager.models import ServiceSettings
from service_manager.models import get_service_settings
from state_monitor.models import get_monitor_settings
from state_monitor.models import MonitorSettings
from django.http import HttpRequest
from ts_adapter import views as ts_adapter_views

    
start_flag=1
stop_flag=0

def call_ts_adapter_before_ffmepg(res_type, src_addr):
    if res_type == 'broadband':
        return 
    service_settings = get_service_settings()   
    request = HttpRequest()
    request.GET ={}
    request.GET['mode'] = 'ip2ts'
    if src_addr[:6] == 'smt://':
        request.GET['src_addr'] = src_addr[6:]
    else:
        request.GET['src_addr'] = src_addr
    request.GET['dest_addr'] = service_settings.auto_ts_adapter_destaddr 
    request.GET['mode'] = 'ip2ts' 
    request.GET['auto_start'] = False 
    ts_adapter_views.modify_item(request)
    ts_adapter_views.start(request)

def call_ts_adapter_after_ffmepg(res_type, src_addr):
    if res_type == 'broadband':
        return 
    service_settings = get_service_settings()   
    request = HttpRequest()
    request.GET ={}
    request.GET['mode'] = 'ip2ts'
    if src_addr[:6] == 'smt://':
        request.GET['src_addr'] = src_addr[6:]
    else:
        request.GET['src_addr'] = src_addr
    request.GET['dest_addr'] = service_settings.auto_ts_adapter_destaddr 
    ts_adapter_views.stop(request)


def start_programs(request):
    service_settings = get_service_settings()   
    monitor_settings = get_monitor_settings()   
    callbacks = {}
    if service_settings.auto_ts_adapter_destaddr != '':
        callbacks['before_ffmpeg'] = call_ts_adapter_before_ffmepg
        callbacks['after_ffmpeg'] = call_ts_adapter_after_ffmepg
    t= threading.Thread(target=start_smt_system,name='smt',args=(service_settings.programs, 
                                                                 service_settings.signal_destip, 
                                                                 service_settings.signal_port,
                                                                 service_settings.resource_broadcast_ip, 
                                                                 service_settings.resource_broadband_ip,
                                                                 monitor_settings.info_collector_ip,
                                                                 monitor_settings.info_collector_port,
                                                                 request.get_host(),
                                                                 callbacks))
    t.setDaemon(True)
    t.start()
    #start_smt_system()
    return HttpResponse('OK')

def show_programs(request):
    return render(request, 'smt_program_server.html', {'programmers': signal_server.programmers})


def start_server(request):
  global start_flag
  global stop_flag
  if start_flag==1:
     start_flag=0
     stop_flag=1
     print "start_server"
     start_programs(request)
  return HttpResponse(u"ok", content_type='application/json')
def stop_server(request):
  global start_flag
  global stop_flag
  if stop_flag==1:
     start_flag=1
     stop_flag=0
     print "stop_server"
     stop_all()
  return HttpResponse(u"ok", content_type='application/json')
