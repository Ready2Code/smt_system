# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.shortcuts import render
from service_manager.models import ServiceSettings

def start_page(request):
    service_settings = ServiceSettings.objects.get(name="default")
    return render(request, 'startpage.html', {'service_settings':service_settings})

