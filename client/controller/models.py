# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models

class ControllerSettings(models.Model):
    controller_name     = models.CharField(max_length=30)
    info_collector_ip   = models.CharField(max_length=30)
    info_collector_port = models.IntegerField()
    info_websocket_ip   = models.CharField(max_length=30)
    info_websocket_port = models.IntegerField()

def get_controller_settings():
    all_settings =  ControllerSettings.objects.all()
    settings = 0
    if len(all_settings) == 0:
        settings,created = ControllerSettings.objects.get_or_create(controller_name     ="default", 
                                                                 info_collector_ip='127.0.0.1',
                                                                 info_collector_port=10100, 
                                                                 info_websocket_ip='127.0.0.1',
                                                                 info_websocket_port=10100) 
    else:
        settings = all_settings[0]
    return settings 

