# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models

class MonitorSettings(models.Model):
    monitor_name        = models.CharField(max_length=30)
    info_collector_ip   = models.CharField(max_length=30)
    info_collector_port = models.IntegerField()
    info_websocket_ip   = models.CharField(max_length=30)
    info_websocket_port = models.IntegerField()

def get_monitor_settings():
    all_settings =  MonitorSettings.objects.all()
    settings = 0
    if len(all_settings) == 0:
        settings,created = MonitorSettings.objects.get_or_create(monitor_name     ="default", 
                                                                 info_collector_ip='127.0.0.1',
                                                                 info_collector_port=7777, 
                                                                 info_websocket_ip='127.0.0.1',
                                                                 info_websocket_port=7778) 
    else:
        settings = all_settings[0]
    return settings 
