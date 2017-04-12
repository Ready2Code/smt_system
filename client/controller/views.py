# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.shortcuts import render

import signal_client
is_running = False
def start_controller(request):
    global is_running
    if not is_running:
        signal_client.initial()
        is_running = True
    return HttpResponse(u"欢迎光临!", type='Application/json')

def handle_command(request):
    signal_client.handle_command(request.GET['command'])
    return HttpResponse(u"2!")

def show_channels(request):
    return render(request, 'show_channels.html', signal_client.channel_info)

def play_channel(request, id):
    signal_client.handle_command("cplay " + id)
    return HttpResponse(u"OK", type='Application/json')

