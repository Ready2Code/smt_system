# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.shortcuts import render
from django.http import HttpResponse

from signal_server import start_smt_system
import threading
from service_manager.models import ServiceSettings
from service_manager.models import get_service_settings
from state_monitor.models import get_monitor_settings
from state_monitor.models import MonitorSettings


    

def start_programs(request):
    service_settings = get_service_settings()   
    monitor_settings = get_monitor_settings()   
#    t= threading.Thread(target=start_smt_system,name='smt',args=('../related/programmes.json','192.168.1.41', 10100, '192.168.1.41', '192.168.1.22'))
    t= threading.Thread(target=start_smt_system,name='smt',args=(service_settings.programs, 
                                                                 service_settings.signal_destip, 
                                                                 service_settings.signal_port,
                                                                 service_settings.resource_broadcast_ip, 
                                                                 service_settings.resource_broadband_ip,
                                                                 monitor_settings.info_collector_ip,
                                                                 monitor_settings.info_collector_port),
                                                                 request.get_host())
    t.setDaemon(True)
    t.start()
    #start_smt_system()
    return HttpResponse('OK')

def show_programs(request):
    return render(request, 'smt_program_server.html', {'programmers': signal_server.programmers})



