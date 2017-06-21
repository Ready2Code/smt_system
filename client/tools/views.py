# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.shortcuts import render
from django.http import HttpResponse
import socket
import json

str_render = {"type" : "render", "format" : {"name" : ""}}

def tools(request):
    return render(request, 'tools.html')

def addr_str_to_tuple(addr):
    pos = addr.find(':')
    if -1 == pos:
        return ('127.0.0.1',1)
    addr_tuple =  (addr[:pos], int(addr[pos+1:]))
    return addr_tuple 

def video_render(request):
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    addr1 = request.GET['addr1']
    addr2 = request.GET['addr2']
    addr3 = request.GET['addr3']
    addr4 = request.GET['addr4']
    addr5 = request.GET['addr5']
    json_cmd = json.dumps(str_render)
    s.sendto(json_cmd, addr_str_to_tuple(addr1))
    s.sendto(json_cmd, addr_str_to_tuple(addr2))
    s.sendto(json_cmd, addr_str_to_tuple(addr3))
    s.sendto(json_cmd, addr_str_to_tuple(addr4))
    s.sendto(json_cmd, addr_str_to_tuple(addr5))
    return HttpResponse(u"ok", content_type='application/json')

