# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.shortcuts import render
from django.http import HttpResponse

from signal_server import start_smt_system
import threading
from models import ServiceSettings

#service_settings.save()

def get_service_settings():
    all_settings =  ServiceSettings.objects.all()
    service_settings = 0
    if len(all_settings) == 0:
        service_settings,created = ServiceSettings.objects.get_or_create(name="default", programs='../related/programmes.json' , signal_destip='127.0.0.1',signal_port=10100, resource_broadcast_ip='127.0.0.1',resource_broadband_ip='127.0.0.1')
    else:
        service_settings = all_settings[0]
    return service_settings 
    

def start_programs(request):
    service_settings = get_service_settings()   
#    t= threading.Thread(target=start_smt_system,name='smt',args=('../related/programmes.json','192.168.1.41', 10100, '192.168.1.41', '192.168.1.22'))
    t= threading.Thread(target=start_smt_system,name='smt',args=(service_settings.programs, service_settings.signal_destip, service_settings.signal_port,service_settings.resource_broadcast_ip, service_settings.resource_broadband_ip))
    t.setDaemon(True)
    t.start()
    #start_smt_system()
    return HttpResponse('OK')

def show_programs(request):
    return render(request, 'smt_program_server.html', {'programmers': signal_server.programmers})


def modify_service_settings(request):
    service_settings = get_service_settings()   
    service_settings.signal_destip   = request.GET['signal_destip']
    service_settings.signal_port     = request.GET['signal_port']
    service_settings.resource_broadcast_ip   = request.GET['resource_broadcast_ip']
    service_settings.resource_broadband_ip   =request.GET['resource_broadband_ip']
    service_settings.programs                = request.GET['programs_file_path']
    service_settings.save()
    return HttpResponse(u"ok", content_type='application/json')
        


