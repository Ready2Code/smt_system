# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models

class TsAdapterSettings(models.Model):
    src_addr   = models.CharField(max_length=30)
    dest_addr  = models.CharField(max_length=30)


