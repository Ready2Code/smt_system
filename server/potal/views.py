# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from utils import functions

from django.shortcuts import render
from service_manager.models import ServiceSettings
from service_manager.models import get_service_settings
from state_monitor.models import get_monitor_settings
from state_monitor.models import MonitorSettings
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
import os
import json
import codecs
from collections import OrderedDict
def start_page(request):
    #service_settings = ServiceSettings.objects.get(name="default")
    monitor_settings = get_monitor_settings()
    service_settings = get_service_settings()
   
    return render(request, 'startpage.html', {'service_settings':service_settings, 'monitor_settings':monitor_settings})

def config_program(request):
    return render(request, 'config_program.html')
	
def modify_service_settings(request):
    global programmes_path
    service_settings = get_service_settings()   
    service_settings.signal_destip   = request.GET['signal_destip']
    service_settings.signal_port     = request.GET['signal_port']
    service_settings.resource_broadcast_ip   = request.GET['resource_broadcast_ip']
    service_settings.resource_broadband_ip   =request.GET['resource_broadband_ip']
    service_settings.programs                = request.GET['programs_file_path']
    service_settings.resource_file_path      = request.GET['resource_file_path']
    service_settings.auto_ts_adapter_destaddr      = request.GET['auto_ts_adapter_destaddr']
    service_settings.broadcast_max_bandwidth      = request.GET['broadcast_max_bandwidth']
    service_settings.save()

    monitor_settings = get_monitor_settings()   
    monitor_settings.info_collector_ip      = request.GET['info_collector_ip']
    monitor_settings.info_collector_port    = request.GET['info_collector_port']
    monitor_settings.info_websocket_ip      = request.GET['info_websocket_ip']
    monitor_settings.info_websocket_port    = request.GET['info_websocket_port']
    monitor_settings.save()
 
    return HttpResponse(u"ok", content_type='application/json')
def get_config_file(request):
    filepath=request.GET["path"].encode('UTF8')
    service_settings_info = get_service_settings()
    print  service_settings_info.programs
    if filepath=='programmes.json':
	   filepath=service_settings_info.programs
    filepath2 = functions.url2pathname(filepath)
    file=codecs.open(filepath2,'r','utf-8')
    data = ''
    try:
       data=file.read()
    finally:
       file.close()
       return HttpResponse(json.dumps(data, ensure_ascii=False), content_type='application/json')
@csrf_exempt
def set_config_file(request):
    data=request.POST["text"].encode('UTF8')
    filepath=request.POST["path"].encode('UTF8')
    service_settings_info = get_service_settings()
    if filepath=='programmes.json':
	   filepath=service_settings_info.programs
    print filepath
    data=json.dumps(json.loads(data,object_pairs_hook=OrderedDict),ensure_ascii=False,indent=4,sort_keys=False)
    filepath2 = functions.url2pathname(filepath)
    file=codecs.open(filepath2,'w','utf-8')
    try:
       data=file.write(data)
    finally:
       file.close()
       filepath=""
    return HttpResponse(u"true", content_type='application/json')
def get_file_list(request):
    allpath=''
    print "*****************service setting rootdir*************/"
    service_settings_rootdir = get_service_settings()
#    rootdir=request.GET["rootdir"].encode('UTF8')
    rootdir=service_settings_rootdir.resource_file_path
    print  rootdir
    for root,dirs,files in os.walk(rootdir):
       for file in files:
         path=os.path.join(root,file)
         if "program.json" in path:
            if "program.json" == os.path.basename(path):
               allpath+=(functions.pathname2url(path)+";")
    return HttpResponse(json.dumps(allpath), content_type='application/json')
def get_broadcast_max_bandwidth( request):
   service_settings_bandwidth = get_service_settings()
   bandwidth=service_settings_bandwidth.broadcast_max_bandwidth
   return HttpResponse(json.dumps(bandwidth), content_type='application/json')

