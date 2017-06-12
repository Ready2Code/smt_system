# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.shortcuts import render
from service_manager.models import ServiceSettings
from service_manager.models import get_service_settings
from state_monitor.models import get_monitor_settings
from state_monitor.models import MonitorSettings
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
import simplejson
import json
def start_page(request):
    #service_settings = ServiceSettings.objects.get(name="default")
    monitor_settings = get_monitor_settings()
    service_settings = get_service_settings()
   
    return render(request, 'startpage.html', {'service_settings':service_settings, 'monitor_settings':monitor_settings})

def config_program(request):
    return render(request, 'config_program.html')
	
def modify_service_settings(request):
    service_settings = get_service_settings()   
    service_settings.signal_destip   = request.GET['signal_destip']
    service_settings.signal_port     = request.GET['signal_port']
    service_settings.resource_broadcast_ip   = request.GET['resource_broadcast_ip']
    service_settings.resource_broadband_ip   =request.GET['resource_broadband_ip']
    service_settings.programs                = request.GET['programs_file_path']
    service_settings.save()

    monitor_settings = get_monitor_settings()   
    monitor_settings.info_collector_ip      = request.GET['info_collector_ip']
    monitor_settings.info_collector_port    = request.GET['info_collector_port']
    monitor_settings.info_websocket_ip      = request.GET['info_websocket_ip']
    monitor_settings.info_websocket_port    = request.GET['info_websocket_port']
    monitor_settings.save()
 
    return HttpResponse(u"ok", content_type='application/json')
def get_config_file(request):
    file=open('../related/programmes.json')
    try:
       data=file.read()
    finally:
       file.close()
       print data
       return HttpResponse(json.dumps(data), content_type='application/json')
@csrf_exempt
def set_config_file(request):
    data=request.POST["text"].encode('UTF8')
    print data
    file=open('../related/programmes.json','w')
    try:
       data=file.write(data)
    finally:
       file.close()
    return HttpResponse(u"true", content_type='application/json')
   
