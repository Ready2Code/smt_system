# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models

class NtpClientSettings(models.Model):
    ntp_client_name     = models.CharField(max_length=30)
    ntp_server_ip       = models.CharField(max_length=30)
    update_interval     = models.IntegerField()

def get_ntpclient_settings():
    all_settings =  NtpClientSettings.objects.all()
    settings = 0
    if len(all_settings) == 0:
        settings,created = NtpClientSettings.objects.get_or_create(ntp_client_name     ="default", 
                                                                   ntp_server_ip='127.0.0.1',
                                                                   update_interval=10) 
    else:
        settings = all_settings[0]
    return settings 

