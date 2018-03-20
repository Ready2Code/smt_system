# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.http import HttpResponse
from django.shortcuts import render
from models import TsAdapterSettings
from django.http import HttpRequest
from django.core import serializers
import MMTtool
import json

def ts_adapter(request):
#   if "username" in request.COOKIES:
      selected_mode         = request.GET['mode']
      return render(request, 'ts_adapter.html',{'mode': selected_mode})
   #else:
    # url='/ts_adapter/?mode=ip2ts'
     #return render(request,'login.html',{'url':url})
def update_list(request):
    all_items = TsAdapterSettings.objects.all()
    json_str = '[]'
    if all_items:
        json_str = serializers.serialize("json",all_items)
    print json_str
    return HttpResponse(json_str, content_type='application/json')

def modify_item(request):
    srcaddr         = request.GET['src_addr']
    destaddr         = request.GET['dest_addr']
    autoStart         = request.GET['auto_start']
    mode         = request.GET['mode']
    if autoStart=='true':
      autoStart=True
    else:
      autoStart=False
    try:
        item = TsAdapterSettings.objects.get(src_addr=srcaddr)
    except:
        item = TsAdapterSettings(src_addr = srcaddr)
    item.dest_addr = destaddr
    item.auto_start = autoStart
    item.mode = mode
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

def find(request):
    try:
        srcaddr         = request.GET['src_addr']
    except:
        srcaddr = ""
    txt = MMTtool.find_ts_adapter(srcaddr)
    ret = {}
    ret["srcaddr"] = srcaddr
    ret["status"] = "on"
    if '' == txt or None == txt:
        ret["status"] = "off"
    return HttpResponse(json.dumps(ret), content_type='application/json')

def auto_start(request):
    all_items = TsAdapterSettings.objects.all()
    try:
        for item in all_items:
           if item.auto_start:
              request = HttpRequest()
              request.GET['mode'] = item.mode
              request.GET['src_addr'] = item.src_addr
              request.GET['dest_addr'] = item.dest_addr
              start(request)
    except:
    	  pass
    return HttpResponse(u"ok", content_type='application/json')


