# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.shortcuts import render
import websocketserver

def show_status(request):
    print request
    return render(request, 'index.html')

def start_state_monitor(request):
    print 'start info server'
    websocketserver.run()
    return HttpResponse('OK', content_type='applicatoin/json')


