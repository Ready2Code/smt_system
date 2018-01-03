# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.shortcuts import render
from django.http import HttpResponse
import json
try:
    from controller import signal_client
except:
    pass
try:
    from service_manager import signal_server
except:
    pass


# Create your views here.
def debug(request):
    print_str         = request.GET['print']
    out_str = eval("'{}'.format("+print_str+")")
    return HttpResponse(out_str, content_type='application/json')


