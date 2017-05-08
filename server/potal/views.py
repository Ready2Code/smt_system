# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.shortcuts import render
from service_manager.models import ServiceSettings
from service_manager.views import get_service_settings

def start_page(request):
    #service_settings = ServiceSettings.objects.get(name="default")
    service_settings = get_service_settings()
    return render(request, 'startpage.html', {'service_settings':service_settings})

