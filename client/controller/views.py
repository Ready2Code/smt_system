# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.shortcuts import render
from django.http import HttpResponse
import json

import signal_client
is_running = False
def start_controller(request):
    global is_running
    if not is_running:
        signal_client.initial()
        is_running = True
    return HttpResponse(u"ok", content_type='application/json')

def handle_command(request):
    signal_client.handle_command(request.GET['command'])
    return HttpResponse(u"ok", content_type='application/json')

def show_channels(request):
    return render(request, 'show_channels.html', signal_client.channel_info)

def play_channel(request, id):
    signal_client.handle_command("cplay " + id)
    return HttpResponse(u"OK", content_type='application/json')

def get_channels(request):
    return HttpResponse(json.dumps(signal_client.channel_info), content_type='application/json')

def get_current_programme_info(request):
    print 'get current programme info'
    ret = signal_client.get_current_programme();
    ret["channel_id"] = signal_client.continue_play_channel 
    return HttpResponse(json.dumps(ret), content_type='application/json')


