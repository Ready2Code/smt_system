# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.shortcuts import render
from django.http import HttpResponse

from signal_server import start_smt_system
import threading

def start_programs(request):
    t= threading.Thread(target=start_smt_system,name='smt',args=(9999,'../related/programmes.json','127.0.0.1'))
    t.setDaemon(True)
    t.start()
    #start_smt_system()
    return HttpResponse('OK')

def show_programs(request):
    return render(request, 'smt_program_server.html', {'programmers': signal_server.programmers})

