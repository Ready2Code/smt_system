# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.shortcuts import render
from django.http import HttpResponse
import socket
import json
VIDEO_RENDER_DEVICE_NUM=5

str_render = {"type" : "render", "format" : {"name" : ""}}

def tools(request):
    return render(request, 'tools.html')

def addr_str_to_tuple(addr):
    pos = addr.find(':')
    if -1 == pos:
        return 0
    addr_tuple =  (addr[:pos], int(addr[pos+1:]))
    return addr_tuple 

def video_render(request):
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    addr_list = []
    for i in range(VIDEO_RENDER_DEVICE_NUM):
        key = 'addr'+str(i)
        addr_list.append(addr_str_to_tuple(request.GET[key]))
    json_cmd = json.dumps(str_render)
    for i in range(VIDEO_RENDER_DEVICE_NUM):
        if 0 != addr_list[i]:
            s.sendto(json_cmd, addr_list[i])
    return HttpResponse(u"ok", content_type='application/json')

