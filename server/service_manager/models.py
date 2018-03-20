# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models

class ServiceSettings(models.Model):
    name      = models.CharField(max_length=30)
    programs  = models.CharField(max_length=80)
    resource_file_path  = models.CharField(max_length=80)
    broadcast_max_bandwidth  = models.CharField(max_length=80)
    signal_destip    = models.CharField(max_length=30)
    signal_port      = models.IntegerField()
    resource_broadcast_ip    = models.CharField(max_length=30)
    resource_broadband_ip    = models.CharField(max_length=30)
    auto_ts_adapter_destaddr = models.CharField(max_length=30)
    aheadtime      = models.IntegerField()
    cachetime      = models.IntegerField()
    signal_format  = models.CharField(max_length=30)

def get_service_settings():
    all_settings =  ServiceSettings.objects.all()
    service_settings = 0
    if len(all_settings) == 0:
        service_settings,created = ServiceSettings.objects.get_or_create(name="default", 
                                                                         programs='../related/programmes.json' , 
                                                                         resource_file_path='/home/' , 
                                                                         broadcast_max_bandwidth='25M' , 
                                                                         signal_destip='127.0.0.1',
                                                                         signal_port=10100, 
                                                                         resource_broadcast_ip='127.0.0.1',
                                                                         resource_broadband_ip='127.0.0.1',
                                                                         auto_ts_adapter_destaddr = '',
																		 aheadtime=2000,
																		 cachetime=6000,
																		 signal_format="program.josn")
    else:
        service_settings = all_settings[0]
    return service_settings 
