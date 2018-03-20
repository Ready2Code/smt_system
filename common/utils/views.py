# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from datetime import datetime
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

class DateTimeEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, datetime):
            return o.isoformat()
        return json.JSONEncoder.default(self, o)

# Create your views here.
def debug(request):
    print_str         = request.GET['print'] if request.GET.has_key('print') else ''
    value = eval(print_str)
    try:
        out_str =json.dumps({print_str:value}, indent=4, cls=DateTimeEncoder) 
    except:
        out_str = eval("'{}'.format("+print_str+")")
    return HttpResponse(out_str, content_type='application/json')


