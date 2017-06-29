# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.http import HttpResponse
from django.shortcuts import render
from models import TsAdapterSettings
from django.core import serializers
import MMTtool
import json

def ts_adapter(request):
    selected_mode         = request.GET['mode']
    return render(request, 'ts_adapter.html',{'mode': selected_mode})

def update_list(request):
    all_items = TsAdapterSettings.objects.all()
    json_str = serializers.serialize("json",all_items)
    return HttpResponse(json_str, content_type='application/json')

def modify_item(request):
    srcaddr         = request.GET['src_addr']
    destaddr         = request.GET['dest_addr']
    try:
        item = TsAdapterSettings.objects.get(src_addr=srcaddr)
    except:
        item = TsAdapterSettings(src_addr = srcaddr)
    item.dest_addr = destaddr
    item.save()
    return HttpResponse(u"ok", content_type='application/json')

def delete_item(request):
    srcaddr         = request.GET['src_addr']
    destaddr         = request.GET['dest_addr']
    try:
        item = TsAdapterSettings.objects.get(src_addr=srcaddr)
        item.delete()
    except:
        pass
    return HttpResponse(u"ok", content_type='application/json')

def start(request):
    mode            = request.GET['mode']
    srcaddr         = request.GET['src_addr']
    destaddr        = request.GET['dest_addr']
    MMTtool.start_ts_adapter(mode, srcaddr, destaddr)
    return HttpResponse(u"ok", content_type='application/json')

def stop(request):
    srcaddr         = request.GET['src_addr']
    MMTtool.stop_ts_adapter(srcaddr)
    return HttpResponse(u"ok", content_type='application/json')
