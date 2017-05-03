# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models

class ServiceSettings(models.Model):
    name      = models.CharField(max_length=30)
    programs  = models.CharField(max_length=80)
    signal_destip    = models.CharField(max_length=30)
    signal_port      = models.IntegerField()
    resource_broadcast_ip    = models.CharField(max_length=30)
    resource_broadband_ip    = models.CharField(max_length=30)
