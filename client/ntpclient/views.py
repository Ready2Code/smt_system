# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.shortcuts import render
from django.http import HttpResponse
from ntpthread import ntpThread
from models import get_ntpclient_settings
import json


ntpthread = ntpThread()

def start_ntpclient(request):
    global ntpthread
    ntpthread.stop()
    ntpthread = ntpThread()
    ntp_server_ip         = request.GET['ntp_server_ip']
    update_interval      = float(request.GET['update_interval'])
    ntpthread.set_ntp_server(ntp_server_ip)
    ntpthread.set_update_interval(float(update_interval))
    ntpclient_settings = get_ntpclient_settings()
    ntpclient_settings.ntp_server_ip = ntp_server_ip 
    ntpclient_settings.update_interval = update_interval 
    ntpclient_settings.save()
    ntpthread.setDaemon(True)
    ntpthread.start()
    return HttpResponse(u"ok", content_type='application/json')

def get_ntpclient_status(request):
    ntp_status = ntpthread.get_ntp_status()
    return HttpResponse(json.dumps(ntp_status), content_type='application/json')
 
def ntpclient_page(request):
    ntpclient_settings = get_ntpclient_settings()
    return render(request, 'ntpclient_page.html', {'ntpclient_settings':ntpclient_settings})
